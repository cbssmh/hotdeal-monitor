from apscheduler.schedulers.blocking import BlockingScheduler
from config import CHECK_INTERVAL_MINUTES
from app import main


def start_scheduler():
    scheduler = BlockingScheduler()

    scheduler.add_job(
        main,
        "interval",
        minutes=CHECK_INTERVAL_MINUTES,
        id="hotdeal_check_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    print(f"스케줄러 시작: {CHECK_INTERVAL_MINUTES}분마다 점검")
    main()  # 시작하자마자 1번 실행

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("스케줄러 종료")
