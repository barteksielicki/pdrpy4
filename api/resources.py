from sanic.response import json
from sanic.exceptions import InvalidUsage

from .app import app


def parse_request_args(request_args, required_args):
    args = dict()
    for arg_name, arg_dict in required_args.items():
        arg = request_args.get(arg_name)
        if not arg:
            if arg_dict['required']:
                raise InvalidUsage(
                    f'{arg_name} is required parameter!',
                    status_code=400,
                )
            continue
        if not isinstance(arg, arg_dict['type_']):
            try:
                arg = arg_dict['type_'](arg)
            except (TypeError, ValueError):
                raise InvalidUsage(
                    f'{arg_name} should be type of {str(arg_dict["type_"])}',
                    status_code=400,
                )
        args[arg_name] = arg
    return args


async def get_records(day, time, line=None):
    db = app.db()
    params = {'day': day, 'time': time}
    if line:
        params['line'] = line
    result = await db.tram_doc.find(params).to_list(None)
    return result


@app.route('/speed')
async def speed_endpoint(request):
    request_args = parse_request_args(request.raw_args, {
        'day': {'type_': int, 'required': True},
        'time': {'type_': str, 'required': True},
        'line': {'type_': int, 'required': False},
    })
    result = await get_records(**request_args)
    return json({'records': result})
