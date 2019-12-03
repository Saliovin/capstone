import hashlib
import os
from flask import request, json, Response, Blueprint
from model.model import FileModel, FileSchema
from werkzeug.utils import secure_filename


harvester_api = Blueprint('harvester_api', __name__)
file_schema = FileSchema()


@harvester_api.route('/', methods=['POST'])
def create():
    if 'file' not in request.files:
        resp = custom_response({'Error': 'No file part in request'}, 400)
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = custom_response({'Error': 'No file selected'}, 400)
        resp.status_code = 400
        return resp

    filename = secure_filename(file.filename)
    temp_path = os.path.join(f'{os.path.realpath(".")}{os.sep}temp', filename)
    file.save(temp_path)
    req_data = get_metadata(filename)

    file = FileModel.get_one_file(req_data['md5'])
    if file:
        os.remove(temp_path)
        return custom_response({'Error': 'File uploaded is a duplicate'}, 400)

    path = os.path.join(f'{os.path.realpath(".")}{os.sep}downloads', filename)
    os.rename(temp_path, path)
    data = file_schema.load(req_data)
    file = FileModel(data)
    file.save()
    return custom_response({'Message': 'File uploaded successfully'}, 201)


@harvester_api.route('/', methods=['GET'])
def get_all():
    files = FileModel.get_all_files()
    ser_file = file_schema.dump(files, many=True)
    return custom_response(ser_file, 200)


@harvester_api.route('/<string:hash_str>', methods=['GET'])
def get_one(hash_str):
    file = FileModel.get_one_file(hash_str)
    if not file:
        return custom_response({'Error': 'File not found'}, 404)
    ser_file = file_schema.dump(file)
    return custom_response(ser_file, 200)


@harvester_api.route('/<string:hash_str>', methods=['PUT'])
def update(hash_str):
    req_data = request.get_json()
    data = file_schema.load(req_data, partial=True)
    file = FileModel.get_one_file(hash_str)
    if not file:
        return custom_response({'Error': 'File not found'}, 404)
    file.update(data)
    ser_file = file_schema.dump(file)
    return custom_response(ser_file, 200)


@harvester_api.route('/<string:hash_str>', methods=['DELETE'])
def delete(hash_str):
    file = FileModel.get_one_file(hash_str)
    if not file:
        return custom_response({'Error': 'File not found'}, 404)
    ser_file = file_schema.dump(file)
    file.delete()

    try:
        path = f'{os.path.realpath(".")}{os.sep}downloads'
        file_path = os.path.join(path, ser_file['filename'])
        os.remove(file_path)
    except FileNotFoundError:
        return custom_response({'Message': 'File missing from disk. File deleted from database'}, 201)

    return custom_response({'Message': 'File deleted from disk and database'}, 201)


def custom_response(res, status_code):
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )


def get_hash(file_path):
    """
    Return md5 and sha1 hashes of the file.

    :param file_path: Full path of the file.
    :return: md5 and sha1 hashes of the file.
    """
    block_size = 65536
    md5_hasher = hashlib.md5()
    sha1_hasher = hashlib.sha1()

    try:
        with open(file_path, 'rb') as f:
            block = f.read(block_size)
            while len(block) > 0:
                md5_hasher.update(block)
                sha1_hasher.update(block)
                block = f.read(block_size)
    except Exception:
        return "Error", "Error"

    return md5_hasher.hexdigest(), sha1_hasher.hexdigest()


def get_metadata(file):
    path = os.path.join(f'{os.path.realpath(".")}{os.sep}temp', file)
    hashes = get_hash(path)
    metadata = {'size': str(os.stat(path).st_size),
                'md5': hashes[0],
                'sha1': hashes[1],
                'filename': file,
                'filetype': file.split('.')[-1]}
    return metadata
