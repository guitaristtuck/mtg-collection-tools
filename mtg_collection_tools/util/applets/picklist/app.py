import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import cast

import requests
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QKeyEvent, QPalette, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStyleFactory,
    QVBoxLayout,
    QWidget,
)

from mtg_collection_tools.util.models.config import CollectionProvider
from mtg_collection_tools.util.models.mtg import Deck
from mtg_collection_tools.util.providers.base import BaseProvider


def is_dark_mode() -> bool:
    """Detect if the system is using dark mode"""
    app = QApplication.instance()
    if app is None or not isinstance(app, QApplication):
        return False
    
    # Get the current palette
    palette = app.palette()
    
    # Check if the window background is dark
    window_color = palette.color(QPalette.ColorRole.Window)
    
    # Calculate luminance (perceived brightness)
    # Using the standard luminance formula: 0.299*R + 0.587*G + 0.114*B
    luminance = (0.299 * window_color.red() + 
                 0.587 * window_color.green() + 
                 0.114 * window_color.blue()) / 255
    
    # If luminance is less than 0.5, consider it dark mode
    return luminance < 0.5


def apply_dark_theme(app: QApplication):
    """Apply a dark theme palette to the application"""
    dark_palette = QPalette()
    
    # Dark theme colors
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(dark_palette)


def apply_light_theme(app: QApplication):
    """Apply a light theme palette to the application"""
    light_palette = QPalette()
    
    # Light theme colors (default Qt colors)
    light_palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    light_palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    light_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    light_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    light_palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    light_palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    light_palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
    light_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    light_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(light_palette)


def setup_theme(app: QApplication):
    """Setup the application theme - always use dark mode"""
    # Use Fusion style for better cross-platform consistency
    app.setStyle(QStyleFactory.create("Fusion"))
    
    # Always apply dark theme
    apply_dark_theme(app)


class BulkImageDownloader(QThread):
    """Thread for downloading all card images in parallel with progress"""
    progress_updated = pyqtSignal(int, int)  # current, total
    download_complete = pyqtSignal()
    
    def __init__(self, card_ids: list[str], max_workers: int = 10):
        super().__init__()
        self.card_ids = card_ids
        self.downloaded_images = {}
        self.max_workers = max_workers
        
    def download_single_image(self, card_id: str) -> tuple[str, QPixmap | None]:
        """Download a single image and return (card_id, pixmap)"""
        try:
            # Construct the Scryfall image URL
            url = f"https://api.scryfall.com/cards/{card_id}?format=image&version=normal"
            response = requests.get(url)
            response.raise_for_status()
            
            # Create QPixmap from the image data
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            
            return card_id, pixmap
        except Exception as e:
            print(f"Failed to download image for card {card_id}: {e}")
            return card_id, None
        
    def run(self):
        total = len(self.card_ids)
        completed = 0
        
        # Use ThreadPoolExecutor for parallel downloads
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_card_id = {
                executor.submit(self.download_single_image, card_id): card_id 
                for card_id in self.card_ids
            }
            
            # Process completed downloads as they finish
            for future in as_completed(future_to_card_id):
                card_id, pixmap = future.result()
                if pixmap is not None:
                    self.downloaded_images[card_id] = pixmap
                
                completed += 1
                self.progress_updated.emit(completed, total)
        
        # Emit completion signal
        self.download_complete.emit()


class ImageDownloader(QThread):
    """Thread for downloading card images in the background"""
    image_downloaded = pyqtSignal(str, QPixmap)  # card_id, pixmap
    
    def __init__(self, card_id: str):
        super().__init__()
        self.card_id = card_id
        
    def run(self):
        try:
            # Construct the Scryfall image URL
            url = f"https://api.scryfall.com/cards/{self.card_id}?format=image&version=normal"
            response = requests.get(url)
            response.raise_for_status()
            
            # Create QPixmap from the image data
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            
            # Emit the signal with the downloaded image
            self.image_downloaded.emit(self.card_id, pixmap)
        except Exception as e:
            print(f"Failed to download image for card {self.card_id}: {e}")


def sort_deck(deck: Deck) -> Deck:
    """Sort the deck by set code and then card name"""
    deck.cards.sort(key=lambda x: (x.set_code, x.name))
    return deck


class DeckPicker(QWidget):
    def __init__(self, deck_id: str, provider: BaseProvider, parent=None):
        super(DeckPicker, self).__init__(parent)
        self.deck_id = deck_id
        self.provider = provider
        self.deck = sort_deck(deck=self.provider.get_deck(deck_id=deck_id))
        self.card_index = 0
        self.setWindowTitle("Deck Picker")
        
        # Image cache to store downloaded images
        self.image_cache = {}
        self.bulk_downloader = None
        
        # Connect the destroyed signal to clean up threads
        self.destroyed.connect(self.cleanup_threads)
        
        # Enable keyboard focus for this widget
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout: QVBoxLayout = QVBoxLayout()

        # Deck name label
        self.deck_name_label = QLabel(f"Deck: {self.deck.name}")
        self.deck_name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.deck_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.deck_name_label)

        # Progress bar for image downloads
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.progress_bar)

        # Card name display (centered above the main content)
        self.card_name_label = QLabel()
        self.card_name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.card_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.card_name_label)

        # Main content area - two columns: card image and set code
        content_layout = QHBoxLayout()
        
        # Card Image (on the left)
        self.card_image_label = QLabel(self)
        self.card_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.card_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_image_label.setMinimumSize(300, 400)
        self.card_image_label.setScaledContents(False)  # Ensure we control scaling manually
        content_layout.addWidget(self.card_image_label)
        
        # Set code and quantity display (large, on the right)
        set_code_layout = QVBoxLayout()
        
        # Set code display (large)
        self.set_code_label = QLabel()
        self.set_code_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.set_code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_code_label.setMinimumSize(200, 100)  # Large minimum size for set code
        set_code_layout.addWidget(self.set_code_label)
        
        # Quantity display (underneath set code)
        self.quantity_label = QLabel()
        self.quantity_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.quantity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quantity_label.setMinimumSize(200, 50)  # Smaller minimum size for quantity
        set_code_layout.addWidget(self.quantity_label)
        
        # Collection status display (underneath quantity)
        self.collection_status_label = QLabel()
        self.collection_status_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.collection_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.collection_status_label.setMinimumSize(200, 50)  # Same size as quantity
        set_code_layout.addWidget(self.collection_status_label)
        
        content_layout.addLayout(set_code_layout)
        
        layout.addLayout(content_layout)

        # Navigation Buttons
        nav_layout = QHBoxLayout()
        
        # Previous button
        self.previous_button = QPushButton("Previous")
        self.previous_button.clicked.connect(self.on_previous)
        self.previous_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Card position label
        self.position_label = QLabel()
        self.position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.position_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Next button
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.on_next)
        self.next_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        nav_layout.addWidget(self.previous_button)
        nav_layout.addWidget(self.position_label)
        nav_layout.addWidget(self.next_button)

        layout.addLayout(nav_layout)
        self.setLayout(layout)
        
        # Start bulk downloading all images
        self.start_bulk_download()
        
        # Fetch collection data for all cards
        self.collection_data = {}
        self.fetch_collection_data()
        
        # Start displaying the first card
        self.update_display()
        
        # Set initial fonts
        self.update_fonts()

    def calculate_font_sizes(self) -> dict[str, int]:
        """Calculate dynamic font sizes based on window size"""
        width = self.width()
        height = self.height()
        
        # Base font sizes on window dimensions
        base_size = min(width, height) // 40  # Scale with window size
        base_size = max(base_size, 10)  # Minimum size of 10
        
        return {
            'deck_name': int(base_size * 1.2),      # Larger for deck name
            'card_name': int(base_size * 1.0),      # Standard size for card name
            'set_code': int(base_size * 2.5),       # Very large for set code
            'quantity': int(base_size * 1.2),       # Medium size for quantity
            'collection_status': int(base_size * 1.0), # Same as card name
            'position': int(base_size * 0.9),       # Slightly smaller
            'button': int(base_size * 0.8),         # Smaller for buttons
            'progress': int(base_size * 0.8),       # Same as buttons
        }
    
    def update_fonts(self):
        """Update all font sizes based on current window size"""
        font_sizes = self.calculate_font_sizes()
        
        # Update deck name font
        deck_font = QFont()
        deck_font.setPointSize(font_sizes['deck_name'])
        deck_font.setBold(True)
        self.deck_name_label.setFont(deck_font)
        
        # Update card name font
        card_name_font = QFont()
        card_name_font.setPointSize(font_sizes['card_name'])
        self.card_name_label.setFont(card_name_font)
        
        # Update set code font (very large)
        set_code_font = QFont()
        set_code_font.setPointSize(font_sizes['set_code'])
        set_code_font.setBold(True)
        self.set_code_label.setFont(set_code_font)
        
        # Update quantity font
        quantity_font = QFont()
        quantity_font.setPointSize(font_sizes['quantity'])
        self.quantity_label.setFont(quantity_font)
        
        # Update collection status font
        collection_status_font = QFont()
        collection_status_font.setPointSize(font_sizes['collection_status'])
        self.collection_status_label.setFont(collection_status_font)
        
        # Update position label font
        pos_font = QFont()
        pos_font.setPointSize(font_sizes['position'])
        self.position_label.setFont(pos_font)
        
        # Update button fonts
        button_font = QFont()
        button_font.setPointSize(font_sizes['button'])
        self.previous_button.setFont(button_font)
        self.next_button.setFont(button_font)
        
        # Update progress bar font
        progress_font = QFont()
        progress_font.setPointSize(font_sizes['progress'])
        self.progress_bar.setFont(progress_font)
    
    def resizeEvent(self, a0):
        """Handle window resize events"""
        super().resizeEvent(a0)
        self.update_fonts()
        # Update the image display when the window is resized
        self.update_display()
    
    def keyPressEvent(self, a0: QKeyEvent | None):
        """Handle keyboard shortcuts"""
        if a0 and a0.key() == Qt.Key.Key_Left:
            self.on_previous()
        elif a0 and a0.key() == Qt.Key.Key_Right:
            self.on_next()
        else:
            super().keyPressEvent(a0)
    
    def showEvent(self, a0):
        """Called when the widget is shown - set focus to enable keyboard input"""
        super().showEvent(a0)
        self.setFocus()  # Set focus to this widget when shown

    def update_display(self):
        """Update the display to show the current card"""
        if 0 <= self.card_index < len(self.deck.cards):
            card = self.deck.cards[self.card_index]
            
            # Update card name (centered above)
            self.card_name_label.setText(card.name)
            
            # Update set code (large, on the left)
            self.set_code_label.setText(card.set_code.upper())
            
            # Update quantity (underneath set code)
            self.quantity_label.setText(f"count: {card.quantity}x")
            
            # Update collection status (underneath quantity)
            status_text, status_color = self.get_collection_status_text(card.name)
            self.collection_status_label.setText(status_text)
            self.collection_status_label.setStyleSheet(f"color: rgb({status_color.red()}, {status_color.green()}, {status_color.blue()})")
            
            # Update position label
            self.position_label.setText(f"Card {self.card_index + 1} of {len(self.deck.cards)}")
            
            # Show image if available in cache
            if card.id in self.image_cache:
                pixmap = self.image_cache[card.id]
                # Scale the image to fit within the label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.card_image_label.size(), 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.card_image_label.setPixmap(scaled_pixmap)
            else:
                # Show placeholder or loading message
                self.card_image_label.setText("Loading image...")
    

    
    def on_previous(self):
        """Move to the previous card"""
        if self.card_index > 0:
            self.card_index -= 1
            self.update_display()
    
    def start_bulk_download(self):
        """Start downloading all card images with progress bar"""
        # Get all unique card IDs
        card_ids = list(set(card.id for card in self.deck.cards))
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(card_ids))
        self.progress_bar.setValue(0)
        
        # Start bulk download
        self.bulk_downloader = BulkImageDownloader(card_ids)
        self.bulk_downloader.progress_updated.connect(self.on_progress_updated)
        self.bulk_downloader.download_complete.connect(self.on_bulk_download_complete)
        self.bulk_downloader.start()
    
    def on_progress_updated(self, current: int, total: int):
        """Update progress bar"""
        self.progress_bar.setValue(current)
    
    def on_bulk_download_complete(self):
        """Called when all images are downloaded"""
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Store all downloaded images in cache
        if self.bulk_downloader:
            self.image_cache.update(self.bulk_downloader.downloaded_images)
        
        # Update display to show the first card's image
        self.update_display()
    
    def cleanup_threads(self):
        """Clean up any running download threads"""
        if self.bulk_downloader and self.bulk_downloader.isRunning():
            self.bulk_downloader.quit()
            self.bulk_downloader.wait()
    
    def fetch_collection_data(self):
        """Fetch collection data for all cards in the deck"""
        # Check if the provider has the get_matches_in_collection method
        if hasattr(self.provider, 'get_matches_in_collection'):
            self.collection_data = self.provider.get_matches_in_collection(self.deck.cards)
        else:
            # If provider doesn't support collection checking, set empty data
            self.collection_data = {card.name: {"exact_print_quantity": 0, "other_print_quantity": 0} for card in self.deck.cards}

    
    def get_collection_status_text(self, card_name: str) -> tuple[str, QColor]:
        """Get the collection status text and color for a card"""
        if card_name not in self.collection_data:
            return "Not in collection", QColor(255, 0, 0)  # Red
        
        data = self.collection_data[card_name]
        
        if data["exact_print_quantity"] > 0:
            return f"In collection: {data['exact_print_quantity']}", QColor(0, 255, 0)  # Green
        elif data["other_print_quantity"] > 0:
            return f"Other printings: {data['other_print_quantity']}", QColor(255, 255, 0)  # Yellow
        else:
            return "Not in collection", QColor(255, 0, 0)  # Red
    
    def on_next(self):
        """Move to the next card"""
        if self.card_index < len(self.deck.cards) - 1:
            self.card_index += 1
            self.update_display()


class AppWindow(QMainWindow):
    def __init__(self, deck_id: str, provider: BaseProvider):
        super().__init__()
        self.setWindowTitle("Deck Viewer")
        
        # Set window size and make it resizable
        self.resize(800, 900)
        self.setMinimumSize(600, 700)
        
        # Create deck picker directly
        self.deck_picker = DeckPicker(deck_id=deck_id, provider=provider, parent=self)
        
        # Set up central widget
        self.setCentralWidget(self.deck_picker)
    
    def showEvent(self, a0):
        """Called when the window is shown"""
        super().showEvent(a0)
        # Print window flags for debugging
        print(f"Window flags: {self.windowFlags()}")
        print(f"Window title: {self.windowTitle()}")
        print(f"Window is visible: {self.isVisible()}")


def run_picklist_app(provider: BaseProvider, deck_id: str):
    app = QApplication([])
    setup_theme(app)  # Apply theme before showing the window
    window = AppWindow(deck_id=deck_id, provider=provider)
    
    # Ensure the window is shown as a proper window
    window.setWindowState(Qt.WindowState.WindowActive)
    window.show()
    window.raise_()
    window.activateWindow()
    
    app.exec()
