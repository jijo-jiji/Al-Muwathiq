import uuid
from django.db import models
from django.conf import settings

class SourceDocument(models.Model):
    class Authority(models.TextChoices):
        BNM = 'BNM', 'Bank Negara Malaysia'
        AAOIFI = 'AAOIFI', 'AAOIFI'
        SC = 'SC', 'Securities Commission'
        IIFM = 'IIFM', 'IIFM'
        FATWA = 'FATWA', 'General Fatwas'
        IIFA = 'IIFA', 'International Islamic Fiqh Academy' # Added based on SRS 1.1 FR-01

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    authority = models.CharField(max_length=20, choices=Authority.choices)
    file_path = models.FileField(upload_to='source_documents/')
    source_url = models.URLField(max_length=500, blank=True, null=True, help_text="Original URL of the document")
    publication_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_ingested = models.BooleanField(default=False)
    ingested_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        
        return f"{self.authority} - {self.title}"

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions', null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.id} by {self.user}"

class EvidenceArtifact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_doc = models.ForeignKey(SourceDocument, on_delete=models.CASCADE, related_name='evidence_artifacts')
    page_number = models.IntegerField()
    highlighted_text = models.TextField() # Changed to TextField for potentially long snippets
    image_path = models.ImageField(upload_to='evidence_artifacts/')

    def __str__(self):
        return f"Evidence from {self.source_doc.title} - Page {self.page_number}"

class ChatMessage(models.Model):
    class Sender(models.TextChoices):
        USER = 'USER', 'User'
        AI = 'AI', 'AI'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=Sender.choices)
    text_content = models.TextField()
    evidence_link = models.ForeignKey(EvidenceArtifact, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    timestamp = models.DateTimeField(auto_now_add=True) # Added timestamp for ordering

    def __str__(self):
        return f"{self.sender}: {self.text_content[:50]}..."
