from flask import Blueprint, request, g, jsonify
from dataviva import db
import dataviva.hedu.models as hedu
from dataviva.utils.gzip_data import gzipped
from sqlalchemy import func, distinct, desc
from dataviva.utils import make_query
from dataviva.utils.decorators import cache_api
from dataviva.utils import table_helper, query_helper


mod = Blueprint('hedu', __name__, url_prefix='/hedu')

@mod.route('/<year>/<bra_id>/<university_id>/<course_hedu_id>/')
@gzipped
# @cache_api("hedu")
def hedu_api(**kwargs):
    tables = [hedu.Yb_hedu, hedu.Yc_hedu, hedu.Yu, hedu.Ybc_hedu, hedu.Ybu, hedu.Yuc, hedu.Ybuc]

    idonly = request.args.get('id', False) is not False
    limit = int(request.args.get('limit', 0) or kwargs.pop('limit', 0))
    order = request.args.get('order', None) or kwargs.pop('order', None)
    order_col = order
    sort = request.args.get('sort', None) or kwargs.pop('sort', 'desc')
    serialize = request.args.get('serialize', None) or kwargs.pop('serialize', True)
    exclude = request.args.get('exclude', None) or kwargs.pop('exclude', None)
    download = request.args.get('download', None) or kwargs.pop('download', None)

    if "university_id" in kwargs:
        # -- there is no nesting for university ids
        kwargs["university_id"] = kwargs["university_id"].replace("show.5", "show")

    allowed_when_not, possible_tables = table_helper.prepare(['bra_id', 'university_id', 'course_hedu_id'], tables)
    table = table_helper.select_best_table(kwargs, allowed_when_not, possible_tables)

    filters, groups, show_column = query_helper.build_filters_and_groups(table, kwargs, exclude=exclude)

    results = query_helper.query_table(table, filters=filters, groups=groups, limit=limit, order=order, sort=sort, serialize=serialize)

    if serialize or download:
        response = jsonify(results)
        if download:
            response.headers["Content-Disposition"] = "attachment;filename=hedu_data.json"
        return response

    return results
