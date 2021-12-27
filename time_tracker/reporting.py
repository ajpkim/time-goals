from time_tracker import get_today_status, get_time_str

def generate_today_report(projects_minutes_goals: {str: [int]}) -> str:
    total_time = 0
    report = ""

    for project, (mins, goal) in projects_minutes_goals.items():
        total_time += mins
        mins, goal = get_time_str(mins), get_time_str(goal)
        report += f"{project:<25} {mins:<6} :: {goal}\n"

    total_time = get_time_str(total_time)
    report += ".....\n" + "Total Time".ljust(26) + f"{total_time}\n"
    report = "\n---------- Today's Tracked Time ----------\n" + report
    report += "------------------------------------------"
    return report

def generate_project_report():
    pass


def display_today_status(session):
    data = get_today_status(session)
    report = generate_today_report(data)
    print(report)




def display_project_report(project_name: str, timeframes: [str], minutes: [int]):
    print(f"\n---------- {project_name} ----------")
    report = ""
    for timeframe, mins in zip(timeframes, minutes):
        time_str = get_time_str(mins)
        report = f"{timeframe:<25} {time_str}\n" + report

    print(report)
