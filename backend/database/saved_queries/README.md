# Gym Management System - Database Schema Documentation

This document provides a comprehensive overview of the database schema for the Gym Management System, organizing tables by their purpose and relationships.

## Table of Contents

1. [User Management System](#user-management-system)
2. [Membership & Billing System](#membership--billing-system)
3. [Facility Management](#facility-management)
4. [Training System](#training-system)
5. [Class Management System](#class-management-system)
6. [Scheduling & Live Sessions](#scheduling--live-sessions)
7. [Communication System](#communication-system)
8. [Database Views](#database-views)

---

## User Management System

### Core User Tables

These tables handle user authentication, profiles, and role-based access control.

#### `users`

**Purpose**: Central user table storing basic information for all system users

- **Primary Key**: `user_id`
- **Unique Fields**: `firebase_uid`, `email`
- **User Types**: member, trainer, manager
- **Key Features**: Firebase authentication integration, soft delete with `is_active`

#### `members`

**Purpose**: Extended profile information for gym members

- **Primary Key**: `member_id`
- **Foreign Key**: `user_id` → `users(user_id)`
- **Key Features**: Fitness goals, health conditions, physical metrics
- **Relationship**: One-to-one with users where `user_type = 'member'`

#### `trainers`

**Purpose**: Professional information for gym trainers

- **Primary Key**: `trainer_id`
- **Foreign Key**: `user_id` → `users(user_id)`
- **Key Features**: Specializations, certifications, experience tracking
- **Relationship**: One-to-one with users where `user_type = 'trainer'`

#### `managers`

**Purpose**: Administrative information for gym managers

- **Primary Key**: `manager_id`
- **Foreign Key**: `user_id` → `users(user_id)`
- **Key Features**: Department assignment, hire date tracking
- **Relationship**: One-to-one with users where `user_type = 'manager'`

---

## Membership & Billing System

### Membership Management

Tables that handle membership plans, subscriptions, and member enrollment.

#### `membership_types`

**Purpose**: Define available membership tiers and pricing

- **Primary Key**: `membership_type_id`
- **Key Features**: Tiered pricing (monthly, quarterly, yearly), class limits, custom plan allowances
- **Business Logic**: Controls member access to features based on membership level

#### `memberships`

**Purpose**: Track active and historical memberships for members

- **Primary Key**: `membership_id`
- **Foreign Keys**:
  - `member_id` → `members(member_id)`
  - `membership_type_id` → `membership_types(membership_type_id)`
- **Key Features**: Payment status tracking, auto-renewal, date range management

### Financial Management

#### `financial_transactions`

**Purpose**: Record all financial transactions in the system

- **Primary Key**: `transaction_id`
- **Foreign Key**: `member_id` → `members(member_id)`
- **Transaction Types**: Membership fees, class bookings, cancellation fees, refunds
- **Key Features**: Payment method tracking, transaction status, reference IDs for external payment systems

---

## Facility Management

### Physical Infrastructure

Tables managing the gym's physical spaces and operational hours.

#### `halls`

**Purpose**: Define training spaces and their capabilities

- **Primary Key**: `hall_id`
- **Key Features**: Capacity limits, equipment availability, location tracking
- **Business Logic**: Used for scheduling and resource allocation

#### `gym_hours`

**Purpose**: Define operating hours for each day of the week

- **Primary Key**: `hours_id`
- **Unique Field**: `day_of_week`
- **Key Features**: Holiday management, special notes, closure tracking
- **Business Logic**: Validates scheduling within operational hours

---

## Training System

### Training Content Management

Core tables for creating and managing workout programs.

#### `training_plans`

**Purpose**: Master templates for workout programs

- **Primary Key**: `plan_id`
- **Foreign Key**: `created_by` → `trainers(trainer_id)`
- **Key Features**: Difficulty levels, focus areas, target demographics, custom vs. standard plans
- **Relationship**: One-to-many with `training_plan_days`

#### `training_plan_days`

**Purpose**: Individual workout days within a training plan

- **Primary Key**: `day_id`
- **Foreign Key**: `plan_id` → `training_plans(plan_id)`
- **Key Features**: Day sequencing, focus areas, duration estimates
- **Relationship**: One-to-many with `training_day_exercises`

#### `exercises`

**Purpose**: Exercise library with detailed instructions

- **Primary Key**: `exercise_id`
- **Key Features**: Muscle group targeting, equipment requirements, multimedia resources
- **Business Logic**: Reusable across multiple training plans

#### `training_day_exercises`

**Purpose**: Specific exercise prescriptions within a workout day

- **Primary Key**: `id`
- **Foreign Keys**:
  - `day_id` → `training_plan_days(day_id)`
  - `exercise_id` → `exercises(exercise_id)`
- **Key Features**: Sets, reps, rest periods, exercise ordering

### Member Training Management

#### `member_active_plans`

**Purpose**: Track which training plans members are currently following

- **Primary Key**: `active_plan_id`
- **Foreign Keys**:
  - `member_id` → `members(member_id)`
  - `plan_id` → `training_plans(plan_id)`
- **Key Features**: Plan lifecycle management, date tracking
- **Business Logic**: Ensures members have active training guidance

#### `member_saved_plans`

**Purpose**: Allow members to bookmark training plans for future use

- **Primary Key**: `id`
- **Foreign Keys**:
  - `member_id` → `members(member_id)`
  - `plan_id` → `training_plans(plan_id)`
- **Key Features**: Personal workout library, note-taking

#### `custom_plan_requests`

**Purpose**: Handle requests for personalized training plans

- **Primary Key**: `request_id`
- **Foreign Keys**:
  - `member_id` → `members(member_id)`
  - `assigned_trainer_id` → `trainers(trainer_id)`
  - `completed_plan_id` → `training_plans(plan_id)`
- **Workflow**: Pending → Assigned → In Progress → Completed/Cancelled

### Workout Tracking & Analytics

#### `logged_workouts`

**Purpose**: Record completed workout sessions

- **Primary Key**: `logged_workout_id`
- **Foreign Keys**:
  - `member_id` → `members(member_id)`
  - `member_active_plan_id` → `member_active_plans(active_plan_id)`
  - `training_plan_day_id` → `training_plan_days(day_id)`
  - `live_session_id` → `live_sessions(live_session_id)`
- **Sources**: Self-logged, trainer-logged, or from live sessions
- **Key Features**: Actual duration tracking, session notes

#### `logged_workout_exercises`

**Purpose**: Detailed performance data for each exercise in a workout

- **Primary Key**: `log_exercise_id`
- **Foreign Keys**:
  - `logged_workout_id` → `logged_workouts(logged_workout_id)`
  - `exercise_id` → `exercises(exercise_id)`
  - `training_day_exercise_id` → `training_day_exercises(id)`
- **Key Features**: Prescribed vs. actual performance comparison, set-by-set tracking

---

## Class Management System

### Class Structure

Tables for managing group fitness classes and events.

#### `class_types`

**Purpose**: Define categories of group fitness classes

- **Primary Key**: `class_type_id`
- **Key Features**: Duration standards, difficulty levels, default pricing and capacity
- **Examples**: Yoga, HIIT, Strength Training, Cardio

#### `classes`

**Purpose**: Specific instances of group fitness classes

- **Primary Key**: `class_id`
- **Foreign Keys**:
  - `class_type_id` → `class_types(class_type_id)`
  - `trainer_id` → `trainers(trainer_id)`
  - `hall_id` → `halls(hall_id)`
- **Key Features**: Scheduling, capacity management, pricing, status tracking

#### `class_bookings`

**Purpose**: Member enrollments in specific classes

- **Primary Key**: `booking_id`
- **Foreign Keys**:
  - `class_id` → `classes(class_id)`
  - `member_id` → `members(member_id)`
- **Key Features**: Payment processing, attendance tracking, cancellation management
- **Business Logic**: Enforces capacity limits, handles waitlists

---

## Scheduling & Live Sessions

### Advanced Scheduling System

Tables for personalized training schedules and live session management.

#### `training_preferences`

**Purpose**: Member availability and trainer preferences for personalized scheduling

- **Primary Key**: `preference_id`
- **Foreign Keys**:
  - `member_id` → `members(member_id)`
  - `trainer_id` → `trainers(trainer_id)`
- **Key Features**: Weekly time slot preferences, trainer selection
- **Business Logic**: Input for automated schedule generation

#### `weekly_training_goals`

**Purpose**: Member-defined training objectives for specific weeks

- **Primary Key**: `goal_id`
- **Foreign Key**: `member_id` → `members(member_id)`
- **Key Features**: Session frequency goals, priority levels
- **Business Logic**: Guides schedule optimization algorithms

#### `weekly_schedule`

**Purpose**: Generated weekly training schedules

- **Primary Key**: `schedule_id`
- **Foreign Keys**:
  - `hall_id` → `halls(hall_id)`
  - `trainer_id` → `trainers(trainer_id)`
  - `created_by` → `users(user_id)`
- **Key Features**: Time slot management, capacity tracking, status monitoring

#### `schedule_members`

**Purpose**: Member assignments to scheduled training slots

- **Primary Key**: `id`
- **Foreign Keys**:
  - `schedule_id` → `weekly_schedule(schedule_id)`
  - `member_id` → `members(member_id)`
  - `training_plan_day_id` → `training_plan_days(day_id)`
- **Key Features**: Attendance tracking, specific workout day assignment

### Live Session Management

#### `live_sessions`

**Purpose**: Real-time training session instances

- **Primary Key**: `live_session_id`
- **Foreign Key**: `schedule_id` → `weekly_schedule(schedule_id)`
- **Key Features**: Session timing, status progression, trainer notes
- **Lifecycle**: Started → In Progress → Completed/Cancelled

#### `live_session_attendance`

**Purpose**: Real-time attendance tracking during live sessions

- **Primary Key**: `id`
- **Foreign Keys**:
  - `live_session_id` → `live_sessions(live_session_id)`
  - `member_id` → `members(member_id)`
- **Key Features**: Check-in/check-out times, attendance verification

---

## Communication System

### Notification Management

#### `email_notifications`

**Purpose**: Track email communications sent to users

- **Primary Key**: `notification_id`
- **Foreign Key**: `user_id` → `users(user_id)`
- **Key Features**: Delivery status tracking, categorization, related record linking
- **Use Cases**: Class confirmations, membership reminders, custom plan updates

---

## Database Views

### Analytics & Reporting Views

Pre-computed views for common reporting and dashboard queries.

#### `manager_dashboard_view`

**Purpose**: High-level metrics for management oversight

- **Metrics**: Scheduled classes, completed classes, active members, total revenue

#### `trainer_schedule_view`

**Purpose**: Trainer workload and schedule overview

- **Data**: Upcoming class assignments, hall allocations, time slots

#### `member_activity_view`

**Purpose**: Member engagement and participation summary

- **Metrics**: Classes booked, training sessions scheduled, active plans

#### `revenue_summary_view`

**Purpose**: Financial performance breakdown by transaction type

- **Metrics**: Revenue by category, transaction volumes

#### `available_halls_view`

**Purpose**: Real-time facility availability for scheduling

- **Logic**: Shows unbooked time slots across all halls

#### `available_trainers_view`

**Purpose**: Trainer availability for assignment optimization

- **Logic**: Shows unassigned time slots for all trainers

---

## Key Relationships & Data Flow

### User Journey Flow

1. **Registration**: `users` → `members`/`trainers`/`managers`
2. **Membership**: `members` → `memberships` → `membership_types`
3. **Training Plans**: `training_plans` → `training_plan_days` → `training_day_exercises` → `exercises`
4. **Member Engagement**: `member_active_plans` → `logged_workouts` → `logged_workout_exercises`
5. **Class Participation**: `classes` → `class_bookings` → `financial_transactions`
6. **Personalized Training**: `training_preferences` → `weekly_schedule` → `live_sessions` → `live_session_attendance`

### Business Logic Integration

- **Capacity Management**: `halls.max_capacity` ↔ `classes.max_participants` ↔ `class_bookings` count
- **Membership Benefits**: `membership_types` rules → `class_bookings.payment_status`
- **Schedule Optimization**: `training_preferences` + `weekly_training_goals` → `weekly_schedule` generation
- **Progress Tracking**: `training_day_exercises` (prescribed) ↔ `logged_workout_exercises` (actual)

This schema supports a comprehensive gym management system with features for membership management, class scheduling, personalized training, progress tracking, and business analytics.
