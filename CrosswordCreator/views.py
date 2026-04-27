# CrosswordCreator/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Puzzle
from .utils import CrosswordGenerator  



def home(request):
    return render(request, 'puzzles/home.html')

# ==========================================
# CREATE VIEWS
# ==========================================



def create_crossword(request):
    if request.method == "POST":
        title = request.POST.get('title')
        
        # 1. Grab the lists of inputs from the HTML form arrays
        submitted_words = request.POST.getlist('word[]')
        submitted_clues = request.POST.getlist('clue[]')
        
        # 2. Zip them together into the format the generator needs
        words_and_clues = []
        for word, clue in zip(submitted_words, submitted_clues):
            # Clean up the input (remove spaces, force uppercase for words)
            clean_word = word.strip().upper()
            clean_clue = clue.strip()
            
            # Only add it if they actually typed something
            if clean_word and clean_clue:
                words_and_clues.append({
                    "word": clean_word,
                    "clue": clean_clue
                })
        
        # 3. Initialize your library with the dynamic data
        generator = CrosswordGenerator(words_and_clues, grid_size=15)
        
        # 4. Run the generation algorithm
        result = generator.generate()
        
        # 5. Save it to the database
        puzzle = Puzzle.objects.create(
            title=title,
            rows=15,
            cols=15,
            grid=result['grid'],
            clues=result['clues']
        )
        
        return redirect('play_crossword', code=puzzle.code)

    return render(request, 'puzzles/admin_create.html')



def edit_crossword(request, puzzle_id):
    """
    Where the admin actually builds the grid and adds clues.
    """
    puzzle = get_object_or_404(Puzzle, id=puzzle_id)
    return render(request, 'puzzles/admin_edit.html', {'puzzle': puzzle})


# ==========================================
# PLAYER VIEWS
# ==========================================

def enter_code(request):
    """
    Public landing page where players enter a 6-character code.
    """
    error_message = None
    
    if request.method == "POST":
        # Get the code, strip whitespace, and force uppercase
        entered_code = request.POST.get("code", "").strip().upper()
        
        try:
            # Try to find a puzzle with this exact code
            puzzle = Puzzle.objects.get(code=entered_code)
            
            # If found, redirect them to the actual game board
            return redirect('play_crossword', code=puzzle.code)
            
        except Puzzle.DoesNotExist:
            error_message = "Invalid code. Please check your spelling and try again."
            
    return render(request, 'puzzles/enter_code.html', {'error': error_message})


def play_crossword(request, code):
    """
    The actual game board for the player.
    """
    # Grab the puzzle by its code, or return a 404 error if it somehow doesn't exist
    puzzle = get_object_or_404(Puzzle, code=code)
    
    # Here, you would also query the database for the entries/clues tied to this puzzle
    # entries = Entry.objects.filter(puzzle=puzzle)
    
    context = {
        'puzzle': puzzle,
        # 'entries': entries,
    }
    return render(request, 'puzzles/play.html', context)