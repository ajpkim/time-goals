from time_tracker import get_today_status

def view_today_status():
    today_str = datetime.today().strftime("%Y-%m-%d")
    projects_minutes_goals = get_today_status()
    report = ""




def print_today_report(projects: [str], minutes: [int]):
    total_time = 0
    print("\n--- Today's Tracked Time ---")
    report = ""
    for project, mins in zip(projects, minutes):
        total_time += mins
        time_str = get_time_str(mins)
        report += f"{project:<25} {time_str}\n"

    total_time = get_time_str(total_time)
    report += ".....\n" + "Total Time".ljust(25) + f"{total_time}\n"
    print(report)


def print_project_report(project_name: str, timeframes: [str], minutes: [int]):
    print(f"\n---------- {project_name} ----------")
    report = ""
    for timeframe, mins in zip(timeframes, minutes):
        time_str = get_time_str(mins)
        report = f"{timeframe:<25} {time_str}\n" + report

    print(report)
