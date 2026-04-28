# CrosswordCreator/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Puzzle
from .utils import CrosswordGenerator  
from django.contrib import messages



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
        try:
            result = generator.generate()
        except ValueError as error_message:
            # 3. If it fails, send the error to the frontend and reload the page
            messages.error(request, str(error_message))
            return render(request, 'puzzles/admin_create.html')
        
        # Calculate rows and columns separately
        final_rows = len(result['grid'])
        # Get the length of the first row (the columns), defaulting to 0 if grid is empty
        final_cols = len(result['grid'][0]) if final_rows > 0 else 0 
        
        # 5. Save it to the database with exact dimensions
        puzzle = Puzzle.objects.create(
            title=title,
            rows=final_rows,
            cols=final_cols,  
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