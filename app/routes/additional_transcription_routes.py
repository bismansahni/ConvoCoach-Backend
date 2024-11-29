from flask import Blueprint

from app.controllers.additional_transcription_controller import process_transcription,  \
    upload_recording

additional_transcription_bp=Blueprint('additional_transcription', __name__)




@additional_transcription_bp.route("/upload_recording", methods=["POST"])
def uploader_recording():
    return upload_recording()


@additional_transcription_bp.route("/finalize_transcription", methods=["POST"])
def start_the_transcription():
    return process_transcription()
