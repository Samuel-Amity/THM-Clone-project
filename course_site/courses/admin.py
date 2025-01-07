from django.contrib import admin
from .models import Course, Chapter

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1 

# Course admin with inline chapters
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'coordinator')  
    search_fields = ('title', 'description')  
    list_filter = ('coordinator',) 
    inlines = [ChapterInline]  

class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')  
    search_fields = ('title', 'content')  
    list_filter = ('course',)  

admin.site.register(Course, CourseAdmin)
admin.site.register(Chapter, ChapterAdmin)
