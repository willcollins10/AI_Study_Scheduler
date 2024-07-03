from flask import  jsonify, Blueprint
from model import db, Task, UnschedulableTask
from datetime import datetime, timedelta
import logging
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



# Intervals in adjust_intervals function represent the available or open time slots within a day
# The intervals aren't specific to a task
# I think I just just init these intervals to be the entire day
def adjust_intervals(intervals, start, end):
    # Initialize an empty list to store updated intervals
    updated_intervals = []
    
    # Loop through each interval in the input intervals list
    for interval in intervals:
        # Split the interval string into start and end times, and convert them to datetime objects
        interval_start, interval_end = map(lambda x: datetime.strptime(x, '%H:%M'), interval.split('-'))
        
        # If the interval start is before the task start and the interval end is after the task start,
        # create a new interval from interval_start to the task start
        if interval_start < start < interval_end:
            updated_intervals.append(f"{interval_start.strftime('%H:%M')}-{start.strftime('%H:%M')}")
        
        # If the interval start is before the task end and the interval end is after the task end,
        # create a new interval from the task end to interval_end
        if interval_start < end < interval_end:
            updated_intervals.append(f"{end.strftime('%H:%M')}-{interval_end.strftime('%H:%M')}")
        
        # If the interval does not overlap with the task (i.e., it starts and ends outside the task start and end times),
        # keep the interval unchanged
        if start >= interval_end or end <= interval_start:
            updated_intervals.append(interval)
    
    # Return the list of updated intervals
    return updated_intervals



def load_tasks():
    tasks = Task.query.all()
    fixed_tasks = [task for task in tasks if task.fixed]
    non_fixed_tasks = [task for task in tasks if not task.fixed]
    return fixed_tasks, non_fixed_tasks

# Designed to create an empty schedule for a list of given days
# Takes a single argument days, which is a list of strings
# Each day represents a day you want to initilize the schedule
# Each value is an empty list, which will be used to store tasks for that day
# TODO: Convert to datetime objects for Google Calendar
# TODO: Probably will change this to just be a given week, currently has more functionality this way
def initialize_schedule(days):
    full_day_interval = ['0:00-23:59']
    # Init schedule  dictionary
    # 'tasks' is empty array that will hold the tasks for that day
    # 'intervals' is init to the full 24hrs for each day 
    schedule = {day: {'tasks': [], 'intervals': full_day_interval} for day in days}
    unschedulable_tasks = []
    return schedule, unschedulable_tasks

# This is going to schedule my fixed tasks
# Assuming that we have init the scheudle before this
def schedule_fixed_tasks(schedule, fixed_tasks):
    for task in fixed_tasks:
        day = task.fixed_day
        # This should never happen, but it's here just in case
        if day not in schedule:
            continue
        # Get start & end time of fixed task
        start_time = datetime.strptime(task.fixed_start_time.strftime('%H:%M'), '%H:%M')
        end_time = datetime.strptime(task.fixed_end_time.strftime('%H:%M'), '%H:%M')

        # Add it to the schedule
        schedule[day]['tasks'].append({
            'taskname': task.taskname,
            # Datetime objects are converted to strings
            'start_time': task.fixed_start_time.strftime('%H:%M'), 
            'end_time': task.fixed_end_time.strftime('%H:%M'),
            'fixed': True
        })
        # Adjust the intervals for that day
        schedule[day]['intervals'] = adjust_intervals(schedule[day]['intervals'], start_time, end_time)

    return schedule
     

# Sorts all the tasks that arent fit in descending order of importance, ties broken with difficulty
def sort_nonfix_tasks(non_fixed_tasks):
    return sorted(non_fixed_tasks, key=lambda x: (-x.importance, -x.difficulty))

# To find an open spot in the intervals
# Return start & end times as datetime object if an interval is found
# Else, return none for start and end times
def find_open_spot(intervals, duration):
    # Loop through all of the intervals
    for interval in intervals:
        # Split the interval string into start and end times, and convert them to datetime objects
        start, end = map(lambda x: datetime.strptime(x, '%H:%M'), interval.split('-'))
        
        # Calculate the open duration in minutes between the start and end times
        open_duration = (end - start).total_seconds() // 60
        
        # Check if the open duration is greater than or equal to the task's duration
        # TODO: Get rid of duration as a required field
        if open_duration >= duration:
            # If there's enough open duration, return the start and end times
            return start, end
    
    # If no suitable interval is found, return None for both start and end
    return None, None


# This function attempt to schedule a task
# param schedule: dict - the current schedule
# param task: the task to be scheduled
# param days: list of days to try to schedule the task
# param intervals: list of intervals to try to schedule the task (this will be preferred_intervals)
# param duratin: duration of the task
# return updated schedule & boolean indicated success
# TODO: Fix this because we need to loop for an open interval for the open intervals of that day
def schedule_task(schedule, task, days, intervals, duration):
    # Go through each day
    for day in days:
        # This shouldn't happen, but makes it error proof
        if day not in schedule:
            continue
        
            
        intersect_intervals = get_intersecting_intervals(intervals, schedule[day]['intervals'])
        
        # Try and find an open spot with the given task intervals
        open_start, open_end = find_open_spot(intersect_intervals, duration)
        
        # If find_open_spot() doesn't return None, then we have an open_start
        if open_start:
            # Create a time_delta object to add to open_start to get the end_time
            duration_time = timedelta(minutes=duration)
            # Calculate the end_time by adding open_start to task duration
            end_time = open_start + duration_time
            # Append the task to the days tasks
            schedule[day]['tasks'].append({
                'task_id': task.id,
                'taskname': task.taskname,
                # Converting these two tasks back to strings
                'start_time': open_start.strftime('%H:%M'),
                'end_time': end_time.strftime('%H:%M'),
            })
            schedule[day]['intervals'] = adjust_intervals(schedule[day]['intervals'], open_start, end_time)
            # Task was able to be scheduled, so editied schedule returned
            return schedule, True
    # Task couldn't be scheduled, so no edits to the schedule are made
    return schedule, False

    # Tries to schedule a task in the provided days and intervals, allowing partial scheduling.
    # :param schedule: dict - The current schedule.
    # :param task: Task - The task to be scheduled.
    # :param days: list - List of days to try scheduling the task.
    # :param preferred_intervals: list - List of preferred time intervals to try scheduling the task.
    # :param max_intervals: list - List of maximum time intervals to try scheduling the task.
    # :param duration: int - Duration of the task in minutes.
    # :return: tuple - (updated schedule, boolean indicating success)
def schedule_task_partial(schedule, task, days, preferred_intervals, max_intervals, duration):
    # First see if we can schedule a task within the preferred interval
    # Shouldn't be able to do this, might omit later
   
    for day in days:
        if day not in schedule:
            continue
    
        # Union between available_intervals and max_intervals
        intersecting_intervals = get_intersecting_intervals(max_intervals, schedule[day]['intervals'])


        for interval in intersecting_intervals:
            # Convert each string into a datetime object
            adjust_max_start, adjust_max_end = map(lambda x: datetime.strptime(x, '%H:%M'), interval.split('-'))
            for preferred_interval in preferred_intervals:
                # Convert to datetime objects
                preferred_start, preferred_end = map(lambda x: datetime.strptime(x, '%H:%M'), preferred_interval.split('-'))

                overlap_start = max(preferred_start, adjust_max_start)  
                overlap_end = min(preferred_end, adjust_max_end)

                # This means intervals overlap
                if overlap_start < overlap_end:

                    available_duration = (overlap_end - overlap_start).total_seconds() // 60
                    # Check if the entire duration can fit within the overlap
                    if available_duration >= duration:
                        end_time = overlap_start + timedelta(minutes=duration)
                        # Schedule the task and update the schedule
                        schedule[day]['tasks'].append({
                            'task_id': task.id,
                            'taskname': task.taskname,
                            'start_time': overlap_start.strftime('%H:%M'),
                            'end_time': end_time.strftime('%H:%M'),
                        })
                        schedule[day]['intervals'] = adjust_intervals(schedule[day]['intervals'], overlap_start, end_time)
                        return schedule, True  # Return the updated schedule and success
                    # Find longest possbile duration for each interval
                    interval_duration = (adjust_max_end - adjust_max_start).total_seconds() // 60
                    duration_pref_start = (adjust_max_end - preferred_start).total_seconds() // 60
                    duration_pref_end = (preferred_end - adjust_max_start).total_seconds() // 60

                    # Then we know it's possible to schedule the task
                    if duration <= interval_duration:
                        end_time = adjust_max_start + timedelta(minutes=duration)
                        schedule[day]['tasks'].append({
                            'task_id': task.id,
                            'taskname': task.taskname,
                            'start_time': adjust_max_start.strftime('%H:%M'),
                            'end_time': end_time.strftime('%H:%M'),
                        })
                        schedule[day]['intervals'] = adjust_intervals(schedule[day]['intervals'], adjust_max_start, end_time)
                        return schedule, True



    return schedule, False


def get_intersecting_intervals(input_intervals, available_intervals):
    """
    Determines the intersecting intervals between the input intervals and available intervals for the day.

    :param input_intervals: list - List of input time intervals (preferred or max intervals).
    :param available_intervals: list - List of available time intervals for the day.
    :return: list - List of intersecting intervals.
    """
    intersecting_intervals = []

    for input_interval in input_intervals:
        input_start, input_end = map(lambda x: datetime.strptime(x, '%H:%M'), input_interval.split('-'))
        
        for available_interval in available_intervals:
            available_start, available_end = map(lambda x: datetime.strptime(x, '%H:%M'), available_interval.split('-'))

            # Calculate the overlap between input interval and available interval
            overlap_start = max(input_start, available_start)
            overlap_end = min(input_end, available_end)

            if overlap_start < overlap_end:
                intersecting_intervals.append(f"{overlap_start.strftime('%H:%M')}-{overlap_end.strftime('%H:%M')}")

    return intersecting_intervals


def create_schedule():
    # Create list of days where I will schedule tasks
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Init schedule for scheduled tasks
    # Init unschedulable for uncheduled tasks
    # schedule is a dict with days as keys & dict as values containing 'tasks' and 'intervals'
    # unschedulable is an emppty list that will hold tasks that can't be scheduled
    schedule, unschedulable = initialize_schedule(days)

    # Load the fixed and non_fixed tasks from the database
    # fixed and non_fixed are lists of Task objects
    fixed, non_fixed = load_tasks()

    # Schedule all of the fixed tasks
    schedule = schedule_fixed_tasks(schedule, fixed)

    # Sort non_fixed tasks based on importance and difficutly
    # difficulty used for tie-breakers on importance
    non_fixed_tasks = sort_nonfix_tasks(non_fixed)

    # Schedule the non_fixed tasks
    for task in non_fixed_tasks:
        success = False
        # Try to schedule within preferred_days & preferred_intervals
        if task.preferred_days and task.preferred_intervals:
            schedule, success = schedule_task(schedule, task, task.preferred_days, task.preferred_intervals, task.duration)
        # If that isn't possible, try scheduling withint preferred_days and max_intervals
        if task.preferred_days and task.max_intervals and not success:
            schedule, success = schedule_task_partial(schedule, task, task.preferred_days, task.preferred_intervals, task.max_intervals, task.duration)
        # If that isn't possbible, try scheduinging within all_days and max_intervals, with some overlap in preferred_intervals
        if task.all_days and task.max_intervals and not success:
            schedule, success = schedule_task_partial(schedule, task, task.all_days, task.preferred_intervals, task.max_intervals, task.duration)
        # If that doesn't work, try scheduling within all_days and max_intervals
        if task.all_days and task.max_intervals and not success:
            schedule, success = schedule_task(schedule, task, task.all_days, task.max_intervals, task.duration)
        # If non of it works, add it to the Unschedulable database
        if not success:
            unschedulable.append(task)
            db.session.add(UnschedulableTask(task_id=task.id))
    
    db.session.commit()

    return schedule, unschedulable







