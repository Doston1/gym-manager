This project is a full stack project for Gym Management.
The frontend and the backend are written in Python - the frontend is with NiceGUI and backend with FastAPI, the database is MySQL.

In this app, a user can be - gym member, trainer or a manager.
Authentication and session management is done using Auth0 and storage of the user token in the localStorage.

Logged in gym members have the next use cases:

1. View working hours.
2. Create a training plan - or choose a training plan out of suggested plans.
3. View classes and book them.
4. The most imporant feature:
   a. Every Thursday, all the gym members have 24 hours to choose their preferences for the next week - in which time windows they can schedule a training and which not.
   b. On Friday 00:00 am, the system closes the opportunity to choose preferred time windows and schedules a weekly schedule (Sunday - Saturday) of trainings using data of training halls capacity, trainers available times, and member preferences.
   c. After publishing the schedule, the users have 24 hours to make changes and ask to cancel/change trainings and choose other times.
   d. On Saturday at 00:00 am, the system tries to schedule again a weekly schedule trying to satisfy as many members as possible.
   e. During the week - whenever there is a training, all the users to are registered to the training and the trainer of the training - have access to "Live Training" page that will have a button in the home page.
   f. In the Live Training page - every member can see the training plan for the current training - with details of exercises, number of sets, number of reps for every set and weight.
   g. At the end of the training - every member can change the planned training plan list - to fit the exercises they did in reality - in case they changed some exercises during the training.
   h. Every member can see their process in my plans page, in the training plan that is the main one, they can see the history of training, from the latest one to the first one, in every training they can see which exercises they did, reps, sets, weights.

Logged in gym trainers have the next use cases:

1. View working hours.
2. Log out.
3. training schedule:
   a. Every Saturday see the schedule for the next week - on what times they have trainings schedules and which hall and how many people.
   b. During every training - see the list of members training - with the abillity to see what exercises (with full details) every member has to do.

Logged in gym manager - have the next use cases:

1. View working hours.
2. Log out
3. See the training schedule for this week or next week (on Satruday)
4. Druing trainings - see all of the training halls and for each one - see who is the trainer and who are the trainees (members) with full training info about every member.

The current table schemas are in the file: backend/database/saved_queries/tables_queries.py
The new tables schemas (didn't apply yet, can be changed, but the new code of live_dashboard and weekly_schedule and training_prefereneces already fit those schemas) - in: backend/database/saved_queries/new_tables_queries.py

The code is not ready and nor the implementation, currently only the home page, working hours page, training plans page, my trainings page (not fully), classes page, my bookings page (of classes, not trainings) and first time logging in - full_details page work, and profile - I want to add the implementation or connect the implementation of the training scheduling and live dashboard thing for training details in live.

### Scheduling System:

A friend of mine created a project that accepts students preferences and professors times, and I can use his project (does he have an api?) for my project's trainings scheduling

This is his project:
https://github.com/yazanyehya/Meetly-Project

### Running the program:

1. Backend: uvicorn backend.api:api --host 127.0.0.1 --port 8000 --reload
2. Frontend: python -m frontend.ui
3. database: local mysql database with the correct schemas.
