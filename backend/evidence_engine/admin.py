from django.contrib import admin, messages
from .models import SourceDocument, ChatSession, ChatMessage, EvidenceArtifact
from .ingestion import ingest_document

@admin.action(description='Ingest selected documents into Vector DB')
def ingest_documents(modeladmin, request, queryset):
    count = 0
    for doc in queryset:
        try:
            ingest_document(doc)
            count += 1
        except Exception as e:
            modeladmin.message_user(request, f"Error ingesting {doc.title}: {e}", level=messages.ERROR)
    
    modeladmin.message_user(request, f"Successfully ingested {count} documents.", level=messages.SUCCESS)

@admin.register(SourceDocument)
class SourceDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'authority', 'is_active', 'id')
    list_filter = ('authority', 'is_active')
    search_fields = ('title',)
    actions = [ingest_documents]

@admin.register(EvidenceArtifact)
class EvidenceArtifactAdmin(admin.ModelAdmin):
    list_display = ('source_doc', 'page_number', 'id')
    raw_id_fields = ('source_doc',)

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('timestamp',)

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'started_at')
    inlines = [ChatMessageInline]
