import json
import logging


class BaseSQLStorageMixin(object):
    def _form(self, ConfigCls):
        return ConfigCls(self.config).form()

    def _search(self, SqlCls, ClsName, count, id=None, name=None, session=None, *args, **kwargs):
        if name is None or name == '':
            return []
        nbs = session.query(SqlCls).filter(SqlCls.name.like(lookfor(name))).limit(count)
        return [{'id': ClsName + '-' + str(nb.id), 'name': nb.name} for nb in nbs]

    def _list(self, SqlCls, ListResultCls, setter, req, resp, session, *args, **kwargs):
        resp.content_type = 'application/json'
        result = ListResultCls()
        result.total = session.query(SqlCls).count()
        result.count = min(result.total, 25)
        result.page = 1
        result.pages = int(result.total/result.count) if result.count > 0 else 1

        nbs = session.query(SqlCls).limit(25).all()

        logging.critical('list : {}, result : {} - {}'.format(SqlCls, result.total, len(nbs)))

        setattr(result, setter, [x.to_config(self.config) for x in nbs])
        resp.body = json.dumps(result.to_json())

    def _detail(self, SqlCls, req, resp, session, *args, **kwargs):
        resp.content_type = 'application/json'

        id = justid(req.get_param('id') or -1)
        try:
            id = int(id)
        except ValueError:
            resp.body = '{}'
            return

        if id < 0:
            resp.body = '{}'
            return

        nb_sql = session.query(SqlCls).get(id)
        logging.critical('detail : {}, result : {}'.format(id, nb_sql))

        if nb_sql:
            resp.body = json.dumps(nb_sql.to_config(self.config).edit())
            return
        resp.body = '{}'


def lookfor(s):
    if '*' in s or '_' in s:
        return s.replace('_', '__')\
                .replace('*', '%')\
                .replace('?', '_')
    return '%{0}%'.format(s)


def justid(id):
    if isinstance(id, int):
        return id
    if '-' in id:
        return id.split('-', 1)[-1]
    return id
