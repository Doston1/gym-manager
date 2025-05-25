import enum as py_enum # Python's enum

# This file is for defining Python Enums that can be shared
# by SQLAlchemy models and Pydantic schemas.

class TrainingDayOfWeekEnum(py_enum.Enum):
    Sunday = "Sunday"
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday" 
    Saturday = "Saturday"

class PreferenceTypeEnum(py_enum.Enum):
    Preferred = "Preferred"
    Available = "Available"
    Not_Available = "Not Available"

class ScheduleStatusEnum(py_enum.Enum):
    scheduled = "Scheduled"
    in_progress = "In Progress"
    completed = "Completed"
    cancelled = "Cancelled"

class ScheduleMemberStatusEnum(py_enum.Enum):
    assigned = "Assigned"
    confirmed = "Confirmed"
    cancelled = "Cancelled"
    attended = "Attended"
    no_show = "No Show"

class LiveSessionStatusEnum(py_enum.Enum):
    started = "Started"
    in_progress = "In Progress"
    completed = "Completed"
    cancelled = "Cancelled"

class LiveAttendanceStatusEnum(py_enum.Enum): # Renamed from AttendanceStatusEnum in schemas
    checked_in = "Checked In"
    checked_out = "Checked Out"
    no_show = "No Show"

class TrainingCycleStatusEnum(py_enum.Enum): # Renamed from CycleStatus
    planned = "Planned"
    in_progress = "In Progress"
    completed = "Completed"
    cancelled = "Cancelled"

# Enums from models/training.py (DifficultyLevel, Focus, etc.) should also be here
# if they are Python enums. If they are just strings in the model, that's different.
# For consistency, it's best to define all as Python enums here.

class DifficultyLevelEnum(py_enum.Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Advanced = "Advanced"
    AllLevels = "All Levels"

class FocusEnum(py_enum.Enum):
    WeightLoss = "Weight Loss"
    MuscleGain = "Muscle Gain"
    Endurance = "Endurance"
    Flexibility = "Flexibility"
    Strength = "Strength"
    GeneralFitness = "General Fitness"

class TargetGenderEnum(py_enum.Enum):
    Any = "Any"
    Male = "Male"
    Female = "Female"

class MuscleGroupEnum(py_enum.Enum):
    Chest = "Chest"
    Back = "Back"
    Shoulders = "Shoulders"
    Arms = "Arms"
    Legs = "Legs"
    Core = "Core"
    FullBody = "Full Body"
    Cardio = "Cardio"

class RequestStatusEnum(py_enum.Enum):
    Pending = "Pending"
    Assigned = "Assigned"
    InProgress = "In Progress"
    Completed = "Completed"
    Cancelled = "Cancelled"