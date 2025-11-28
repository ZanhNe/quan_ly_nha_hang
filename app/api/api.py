from flask import Blueprint, request, jsonify, session
from marshmallow import ValidationError
from app.decorator.decorators import login_required, role_required, verification_required
from app.container.container import injector_instance
from app.domain.services.interfaces.interfaces import IBanService
from app.schemas.init_schema import ds_ban_in_schema


api_bp = Blueprint('api', __name__)
ban_service = injector_instance.get(interface=IBanService)


@api_bp.route('/api/v1/bans', methods=['POST'])
@login_required
@verification_required
@role_required('LETAN')
def chon_ban():
    try:
        data = request.get_json()
        print(data)
        letan_id = session.get('user_id')
        ds_ban_in = ds_ban_in_schema.load(data=data['table_ids'])
        ds_ban_out = ban_service.xu_ly_chon_ban(letan_id=letan_id, ban_schemas_in=ds_ban_in)
        return jsonify(ds_ban_out), 200
    except (ValidationError, Exception) as err:
        if isinstance(err, ValidationError):
            print(err)
            return jsonify({'message': str(err)}), 400
        else:
            print(err)
            return jsonify({'message': str(err)}), 400
