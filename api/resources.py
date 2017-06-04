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


async def get_records(
    timestamp_from,
    timestamp_to,
    first_line=None,
    line=None,
):
    db = app.db()
    params = {
        'time': {
            '$gte': timestamp_from,
            '$lte': timestamp_to,
        }
    }
    if first_line or line:
        params['first_line'] = first_line or line
    result = await db.tram_results.find(params, {'_id': 0}).to_list(None)
    return result


@app.route('/speed')
async def speed_endpoint(request):
    request_args = parse_request_args(request.raw_args, {
        'first_line': {'type_': int, 'required': False},
        'line': {'type_': int, 'required': False},
        'timestamp_from': {'type_': int, 'required': True},
        'timestamp_to': {'type_': int, 'required': True},
    })
    result = await get_records(**request_args)
    return json({'records': result})
