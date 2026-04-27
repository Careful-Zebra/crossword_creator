from django.db import models
import random
import string

def generate_unique_code():
    # Generates a random 6-character uppercase code (e.g., "X9B2QM")
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Puzzle(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=6, default=generate_unique_code, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Using integers makes frontend CSS and backend generation math easier
    rows = models.IntegerField(default=15)
    cols = models.IntegerField(default=15) 
    
    # JSONField automatically handles Python dict/list conversion
    grid = models.JSONField(default=list)  
    clues = models.JSONField(default=dict)  

    def __str__(self):
        return self.title