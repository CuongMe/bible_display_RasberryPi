import json
import random
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto

# Load Inky Impression 7.3" display
inky_display = auto()
inky_display.set_border(inky_display.WHITE)

# Load Bible verses from JSON
BIBLE_VERSES_FILE = "bible_verses.json"


def load_verses():
    """Load Bible verses from JSON file."""
    try:
        with open(BIBLE_VERSES_FILE, "r", encoding="utf-8") as file:
            verses = json.load(file)
        return verses
    except Exception as e:
        print(f"Error loading Bible verses: {e}")
        return {}


def get_random_verse(verses):
    """Get a random Bible verse from the loaded data."""
    if not verses:
        return "No verses found.", "Please check the JSON file."

    book, chapter_verse = random.choice(list(verses.items()))
    verse_text = chapter_verse["text"]
    reference = f"{book} {chapter_verse['chapter']}:{chapter_verse['verse']}"
    return reference, verse_text


def display_verse():
    """Render the Bible verse onto the E-Ink display."""
    verses = load_verses()
    reference, verse_text = get_random_verse(verses)

    # Set up the display canvas
    img = Image.new("P", (inky_display.width, inky_display.height), color=inky_display.WHITE)
    draw = ImageDraw.Draw(img)

    # Load fonts (System fonts)
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf", 40)
    font_body = ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/Arial.ttf", 24)

    # Draw verse reference (book + chapter:verse)
    draw.text((30, 30), reference, inky_display.BLACK, font=font_title)

    # Draw the actual verse text, wrapping if needed
    y_offset = 90
    line_spacing = 32
    max_width = inky_display.width - 60  # Padding

    words = verse_text.split()
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        test_width, _ = draw.textsize(test_line, font=font_body)

        if test_width < max_width:
            current_line = test_line
        else:
            draw.text((30, y_offset), current_line, inky_display.BLACK, font=font_body)
            y_offset += line_spacing
            current_line = word  # Start new line with this word

    # Draw last line
    draw.text((30, y_offset), current_line, inky_display.BLACK, font=font_body)

    # Update display
    inky_display.set_image(img)
    inky_display.show()


if __name__ == "__main__":
    display_verse()
