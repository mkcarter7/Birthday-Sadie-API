from django.db import models
from django.contrib.auth.models import User


class TriviaQuestion(models.Model):
    """
    Model for storing trivia questions that can be used in party trivia games.
    """
    party = models.ForeignKey('Party', on_delete=models.CASCADE, related_name='trivia_questions', null=True, blank=True)
    category = models.CharField(max_length=100, default='Personal')
    question = models.TextField()
    option_1 = models.CharField(max_length=200)
    option_2 = models.CharField(max_length=200)
    option_3 = models.CharField(max_length=200, blank=True)
    option_4 = models.CharField(max_length=200, blank=True)
    correct_answer = models.PositiveIntegerField(help_text='Index of correct answer (0-3)')
    points = models.PositiveIntegerField(default=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'question']
        verbose_name = 'Trivia Question'
        verbose_name_plural = 'Trivia Questions'
    
    def __str__(self):
        return f"{self.category}: {self.question[:50]}"
    
    def get_options(self):
        """Return list of options, filtering out empty ones"""
        options = [self.option_1, self.option_2]
        if self.option_3:
            options.append(self.option_3)
        if self.option_4:
            options.append(self.option_4)
        return options
    
    def to_dict(self):
        """Convert to dictionary format for API responses"""
        return {
            'id': self.id,
            'category': self.category,
            'question': self.question,
            'options': self.get_options(),
            'correct_answer': self.correct_answer,
            'points': self.points
        }
