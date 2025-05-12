from django.contrib import admin
from django.contrib import messages
from .models import Student, StudentPackage, Trainer, TrainingPackage, TrainingSession, Tutorial, Course
from vehicles.models import Vehicle
from .utils import assign_sessions  # Import the assignment function

# Action to assign sessions
@admin.action(description="Assign sessions to selected student packages")
def assign_training_sessions(modeladmin, request, queryset):
    for package in queryset:
        if not package.payment_status:
            messages.warning(request, f"⏳ Skipped {package} — Payment not completed.")
            continue
        try:
            assign_sessions(package)
            messages.success(request, f"✅ Sessions assigned for {package}")
        except Exception as e:
            messages.error(request, f"❌ Failed to assign for {package}: {e}")

# Inline TrainingSessions inside StudentPackage
class TrainingSessionInline(admin.TabularInline):
    model = TrainingSession
    extra = 0

# Customize StudentPackage Admin
@admin.register(StudentPackage)
class StudentPackageAdmin(admin.ModelAdmin):
    list_display = ('student', 'package', 'payment_status', 'remaining_sessions')
    inlines = [TrainingSessionInline]
    actions = [assign_training_sessions]  # ✅ Added custom action here

# Register other models normally
admin.site.register(Student)
# admin.site.register(Vehicle)
admin.site.register(Trainer)
admin.site.register(TrainingPackage)
admin.site.register(TrainingSession)
admin.site.register(Tutorial)
admin.site.register(Course)