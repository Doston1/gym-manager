from sqlalchemy.orm import Session
from datetime import date, time, timedelta
from collections import defaultdict
import random
from typing import Optional

from backend.database.crud import training as crud_training
from backend.database.models.training import TrainingPreference, WeeklySchedule, ScheduleMember, Hall, Trainer
from backend.database.schemas.training import WeeklyScheduleCreate, ScheduleMemberCreate, PreferenceType, DayOfWeek as DayOfWeekEnum, ScheduleStatus
from backend.database import SessionLocal, User # Assuming User is needed for created_by

# Configuration (could be moved to a config file or DB)
MIN_MEMBERS_FOR_SESSION = 1 # Minimum members to create a session
DEFAULT_SESSION_DURATION_MINUTES = 90 # Default duration if not specified by preference end_time

def get_next_week_start_date(today: Optional[date] = None) -> date:
    if today is None:
        today = date.today()
    # Next week starts on Sunday. day.weekday(): Mon=0, Sun=6
    days_until_sunday = (6 - today.weekday()) % 7 
    if days_until_sunday == 0 and today.weekday() != 6 : # if today is not sunday but calculation is 0, means next sunday
         days_until_sunday = 7
    elif today.weekday() == 6: # if today is sunday, schedule for next sunday
        days_until_sunday = 7

    next_sunday = today + timedelta(days=days_until_sunday)
    return next_sunday


def run_initial_scheduling():
    """
    Runs on Friday 00:00.
    Schedules trainings for the next week based on member preferences, hall capacity, and trainer availability.
    """
    db: Session = SessionLocal()
    try:
        manager_user_id = 1 # Placeholder for system/manager user ID that creates the schedule
        # Fetch a default manager user or a system user ID
        manager_user = db.query(User).filter(User.user_type == 'manager').first() # Or some specific system user
        if manager_user:
            manager_user_id = manager_user.user_id
        else: # Fallback if no manager found, though this should be handled better
            print("Warning: No manager user found for 'created_by' field in schedule. Using placeholder.")


        target_week_start_date = get_next_week_start_date()
        print(f"Running initial scheduling for week starting: {target_week_start_date}")

        # 1. Clear any existing "Scheduled" entries for the target week to allow fresh scheduling
        # Be cautious with this in production. Maybe only clear if it's the first run for the week.
        db.query(WeeklySchedule).filter(
            WeeklySchedule.week_start_date == target_week_start_date,
            WeeklySchedule.status == ScheduleStatus.scheduled # Only clear non-started ones
        ).delete(synchronize_session=False)
        db.commit()

        # 2. Fetch all preferences for the target week
        preferences = crud_training.get_all_preferences_for_week(db, target_week_start_date)
        if not preferences:
            print("No training preferences found for the target week.")
            return

        # 3. Group preferences by (day, start_time, end_time)
        #    And also by trainer preference if specified
        slot_preferences = defaultdict(lambda: {'members': [], 'trainer_prefs': defaultdict(int)})
        for pref in preferences:
            if pref.preference_type in [PreferenceType.preferred, PreferenceType.available]:
                slot_key = (pref.day_of_week, pref.start_time, pref.end_time)
                slot_preferences[slot_key]['members'].append({
                    'member_id': pref.member_id,
                    'type': pref.preference_type,
                    'preferred_trainer_id': pref.trainer_id
                })
                if pref.trainer_id:
                    slot_preferences[slot_key]['trainer_prefs'][pref.trainer_id] += 1
        
        # 4. Iterate through popular slots and try to schedule
        # Sort slots by number of interested members (descending)
        sorted_slots = sorted(slot_preferences.items(), key=lambda item: len(item[1]['members']), reverse=True)

        for slot_key, data in sorted_slots:
            day_of_week, start_time, end_time = slot_key
            members_data = data['members']
            trainer_preference_counts = data['trainer_prefs']

            if len(members_data) < MIN_MEMBERS_FOR_SESSION:
                continue # Skip if not enough members

            # 5. Find available halls
            available_halls = crud_training.get_halls_available_at_slot(db, target_week_start_date, day_of_week, start_time, end_time)
            if not available_halls:
                print(f"No halls available for {day_of_week.value} {start_time}-{end_time}")
                continue
            
            # 6. Find available trainers
            available_trainers = crud_training.get_trainers_available_at_slot(db, target_week_start_date, day_of_week, start_time, end_time)
            if not available_trainers:
                print(f"No trainers available for {day_of_week.value} {start_time}-{end_time}")
                continue

            # Attempt to match preferred trainer first, then any available trainer
            chosen_trainer_id = None
            if trainer_preference_counts:
                # Sort preferred trainers by preference count
                sorted_preferred_trainers = sorted(trainer_preference_counts.items(), key=lambda item: item[1], reverse=True)
                for pt_id, _ in sorted_preferred_trainers:
                    if any(t.trainer_id == pt_id for t in available_trainers):
                        chosen_trainer_id = pt_id
                        break
            
            if not chosen_trainer_id and available_trainers:
                chosen_trainer_id = random.choice(available_trainers).trainer_id # Simple random choice

            if not chosen_trainer_id:
                print(f"Could not assign a trainer for {day_of_week.value} {start_time}-{end_time}")
                continue

            # Choose a hall (e.g., first available, or smallest that fits, or random)
            # For now, pick the first one that can hold MIN_MEMBERS_FOR_SESSION
            chosen_hall = None
            for hall in sorted(available_halls, key=lambda h: h.max_capacity): # Try smaller halls first
                if hall.max_capacity >= MIN_MEMBERS_FOR_SESSION:
                    chosen_hall = hall
                    break
            
            if not chosen_hall:
                print(f"No suitable hall found for {day_of_week.value} {start_time}-{end_time} with capacity for {len(members_data)} members.")
                continue

            # 7. Create WeeklySchedule entry
            schedule_create = WeeklyScheduleCreate(
                week_start_date=target_week_start_date,
                day_of_week=day_of_week,
                start_time=start_time,
                end_time=end_time,
                hall_id=chosen_hall.hall_id,
                trainer_id=chosen_trainer_id,
                max_capacity=chosen_hall.max_capacity,
                status=ScheduleStatus.scheduled,
                created_by=manager_user_id 
            )
            new_schedule_entry = crud_training.create_weekly_schedule_entry(db, schedule_create)
            print(f"Scheduled: {new_schedule_entry.schedule_id} for {day_of_week.value} {start_time} at Hall {chosen_hall.name} with Trainer {chosen_trainer_id}")

            # 8. Assign members
            assigned_count = 0
            # Prioritize 'Preferred' members
            preferred_members = [m for m in members_data if m['type'] == PreferenceType.preferred]
            available_members = [m for m in members_data if m['type'] == PreferenceType.available]
            
            # Shuffle to give some randomness if many have same preference
            random.shuffle(preferred_members)
            random.shuffle(available_members)

            for member_data in preferred_members:
                if assigned_count < new_schedule_entry.max_capacity:
                    sm_create = ScheduleMemberCreate(
                        schedule_id=new_schedule_entry.schedule_id,
                        member_id=member_data['member_id'],
                        status=ScheduleMemberStatus.assigned
                    )
                    crud_training.add_member_to_schedule_entry(db, sm_create)
                    assigned_count += 1
                else:
                    break
            
            if assigned_count < new_schedule_entry.max_capacity:
                for member_data in available_members:
                    if assigned_count < new_schedule_entry.max_capacity:
                         # Avoid double booking a member at the exact same time slot if they had multiple preferences
                        already_booked = db.query(ScheduleMember).join(WeeklySchedule)\
                            .filter(ScheduleMember.member_id == member_data['member_id'],
                                    WeeklySchedule.week_start_date == target_week_start_date,
                                    WeeklySchedule.day_of_week == day_of_week,
                                    WeeklySchedule.start_time == start_time).first()
                        if not already_booked:
                            sm_create = ScheduleMemberCreate(
                                schedule_id=new_schedule_entry.schedule_id,
                                member_id=member_data['member_id'],
                                status=ScheduleMemberStatus.assigned
                            )
                            crud_training.add_member_to_schedule_entry(db, sm_create)
                            assigned_count += 1
                    else:
                        break
            print(f"Assigned {assigned_count} members to schedule ID {new_schedule_entry.schedule_id}")

        db.commit() # Commit all changes for the week
        print("Initial scheduling complete.")
    except Exception as e:
        db.rollback()
        print(f"Error during initial scheduling: {e}")
    finally:
        db.close()

def run_final_scheduling_adjustments():
    """
    Runs on Saturday 00:00.
    Adjusts the schedule based on member cancellations/changes and tries to optimize.
    This is where adapting Meetly's DFS/BFS for augmenting paths would be beneficial.
    For now, this will be a simpler version focusing on filling gaps from cancellations.
    """
    db: Session = SessionLocal()
    try:
        manager_user_id = 1 # Placeholder
        manager_user = db.query(User).filter(User.user_type == 'manager').first()
        if manager_user:
            manager_user_id = manager_user.user_id

        target_week_start_date = get_next_week_start_date() # Schedule for the upcoming week
        print(f"Running final scheduling adjustments for week starting: {target_week_start_date}")

        # 1. Identify sessions with cancellations or low occupancy
        # For simplicity, let's say we re-evaluate all 'Scheduled' sessions
        
        all_scheduled_sessions = db.query(WeeklySchedule).filter(
            WeeklySchedule.week_start_date == target_week_start_date,
            WeeklySchedule.status == ScheduleStatus.scheduled
        ).all()

        for session in all_scheduled_sessions:
            current_occupancy = db.query(ScheduleMember).filter(
                ScheduleMember.schedule_id == session.schedule_id,
                ScheduleMember.status.notin_([ScheduleMemberStatus.cancelled]) # Count non-cancelled
            ).count()
            
            available_spots = session.max_capacity - current_occupancy

            if available_spots > 0:
                print(f"Session {session.schedule_id} has {available_spots} available spots. Trying to fill.")
                
                # Find members who preferred this slot but weren't assigned, or marked as 'Available'
                # and are not already in ANY session at this specific time.
                
                # Get all members already scheduled at this exact time slot to avoid double booking
                members_already_in_any_session_at_this_time = db.query(ScheduleMember.member_id)\
                    .join(WeeklySchedule, WeeklySchedule.schedule_id == ScheduleMember.schedule_id)\
                    .filter(
                        WeeklySchedule.week_start_date == target_week_start_date,
                        WeeklySchedule.day_of_week == session.day_of_week,
                        WeeklySchedule.start_time == session.start_time,
                        ScheduleMember.status.notin_([ScheduleMemberStatus.cancelled])
                    ).distinct().all()
                
                member_ids_already_booked = [m_id for m_id, in members_already_in_any_session_at_this_time]

                potential_candidates = db.query(TrainingPreference)\
                    .filter(
                        TrainingPreference.week_start_date == target_week_start_date,
                        TrainingPreference.day_of_week == session.day_of_week,
                        TrainingPreference.start_time == session.start_time,
                        TrainingPreference.end_time == session.end_time,
                        TrainingPreference.preference_type.in_([PreferenceType.preferred, PreferenceType.available]),
                        TrainingPreference.member_id.notin_(member_ids_already_booked) # Not already in any session at this time
                    )\
                    .order_by(TrainingPreference.preference_type.desc())\
                    .limit(available_spots * 2).all() # Fetch more candidates than spots to have options
                    
                
                newly_assigned_count = 0
                for candidate_pref in potential_candidates:
                    if newly_assigned_count >= available_spots:
                        break
                    
                    # Check if this member is already in THIS specific session (shouldn't happen if logic is correct above)
                    is_already_in_this_session = db.query(ScheduleMember).filter(
                        ScheduleMember.schedule_id == session.schedule_id,
                        ScheduleMember.member_id == candidate_pref.member_id,
                        ScheduleMember.status.notin_([ScheduleMemberStatus.cancelled])
                    ).count() > 0
                    
                    if not is_already_in_this_session:
                        sm_create = ScheduleMemberCreate(
                            schedule_id=session.schedule_id,
                            member_id=candidate_pref.member_id,
                            status=ScheduleMemberStatus.assigned
                        )
                        crud_training.add_member_to_schedule_entry(db, sm_create)
                        newly_assigned_count += 1
                        print(f"Added member {candidate_pref.member_id} to session {session.schedule_id}")
        
        # TODO: Implement logic for handling member change requests using an adapted DFS/BFS
        # This would involve:
        # 1. A table for `TrainingChangeRequest`.
        # 2. Building a graph of (Member <-> ScheduledSession) with preferences as edge weights/types.
        # 3. For each change request, try to find an augmenting path.

        db.commit()
        print("Final scheduling adjustments complete.")
    except Exception as e:
        db.rollback()
        print(f"Error during final scheduling adjustments: {e}")
    finally:
        db.close()