from celery import shared_task

@shared_task
def process_stream_task(session_id):
    from apps.streaming.models import StreamSession
    # from apps.cv.services import analyze_stream  # потом сделаешь

    session = StreamSession.objects.get(id=session_id)

    try:
        # 🔥 тут будет бесконечный цикл чтения RTSP
        # пока делаем заглушку

        session.status = "running"
        session.save()

    except Exception as e:
        session.status = "error"
        session.error_message = str(e)
        session.save()