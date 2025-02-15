import json
import random
from PIL import Image, ImageDraw, ImageFont
from inky.auto import auto

# Load Inky Impression 7.3" display
inky_display = auto()
inky_display.set_border(inky_display.WHITE)

# Load Bible verses from JSON (list of strings in "Book Chapter:Verse - text" format)
BIBLE_VERSES_FILE = "bible_verses.json"


def load_verses():
    """Load Bible verses from JSON file."""
    try:
        with open(BIBLE_VERSES_FILE, "r", encoding="utf-8") as file:
            verses = json.load(file)
        return verses  # list of strings
    except Exception as e:
        print(f"Error loading Bible verses: {e}")
        return []


def get_random_verse(verses):
    """Get a random Bible verse from the loaded data."""
    if not verses:
        return "No verses found.", "Please check the JSON file."
    verse_line = random.choice(verses)
    try:
        reference, verse_text = verse_line.split(" - ", 1)
    except ValueError:
        reference = ""
        verse_text = verse_line
    return reference, verse_text


def display_verse():
    """Render the Bible verse and additional graphics onto the E-Ink display."""
    # Load a random verse
    verses = load_verses()
    reference, verse_text = get_random_verse(verses)

    # Create the canvas
    img = Image.new("P", (inky_display.width, inky_display.height), color=inky_display.WHITE)
    draw = ImageDraw.Draw(img)

    # Load fonts
    # (Using DejaVu fonts here; adjust paths if necessary)
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    font_blessed = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    font_symbols = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)

    # Top Left: Display Canadian flag image
    try:
        flag = Image.open("canada_flag.png")
        # Resize flag if needed (e.g., to 50x50)
        flag.thumbnail((50, 50))
        img.paste(flag, (10, 10))
    except Exception as e:
        print(f"Error loading flag image: {e}")

    # Top Right: Draw three cross symbols
    cross_text = "✝  ✝  ✝"
    # Measure text width to place at top right with padding
    cross_width, cross_height = draw.textsize(cross_text, font=font_symbols)
    cross_x = inky_display.width - cross_width - 10  # 10 px from right edge
    cross_y = 10  # 10 px from top edge
    draw.text((cross_x, cross_y), cross_text, inky_display.BLACK, font=font_symbols)

    # Center: Bible verse text (reference and verse) in the middle of the display
    # First, combine reference and verse text, then center the block.
    full_text = f"{reference}\n\n{verse_text}"

    # Wrap the text manually (this example uses a simple word-wrap)
    max_width = inky_display.width - 40  # 20px padding on each side
    lines = []
    for paragraph in full_text.split("\n"):
        words = paragraph.split()
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_width, _ = draw.textsize(test_line, font=font_body)
            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        # Add an empty line between paragraphs
        lines.append("")
    # Remove the extra empty line added at the end
    if lines and lines[-1] == "":
        lines.pop()

    # Calculate total height of text block
    line_height = font_body.getsize("Ay")[1] + 5  # adding a little spacing
    text_block_height = len(lines) * line_height
    start_y = (inky_display.height - text_block_height) // 2
    # Draw each line centered
    for i, line in enumerate(lines):
        line_width, _ = draw.textsize(line, font=font_body)
        x = (inky_display.width - line_width) // 2
        y = start_y + i * line_height
        draw.text((x, y), line, inky_display.BLACK, font=font_body)

    # Bottom: Display "Blessed Day" message in bold blue
    blessed_message = "Blessed Day"
    # Blue color in a 1-bit E-Ink: many Inky boards support only black and white, but if your display supports color, you can try:
    blue = (0, 0, 255)  # RGB Blue, adjust if needed
    # Inky displays are usually limited in color - Inky pHAT, for example, is 3-color. Adjust as necessary.
    blessed_width, blessed_height = draw.textsize(blessed_message, font=font_blessed)
    blessed_x = (inky_display.width - blessed_width) // 2
    blessed_y = inky_display.height - blessed_height - 10
    # If your display supports color, use blue; otherwise, this will likely print black.
    draw.text((blessed_x, blessed_y), blessed_message, blue, font=font_blessed)

    # Update display
    inky_display.set_image(img)
    inky_display.show()


if __name__ == "__main__":
    display_verse()
