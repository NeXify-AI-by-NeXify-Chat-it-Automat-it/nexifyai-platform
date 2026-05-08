"""
Supabase Postgres DB Wrapper for NeXifyAI Backend.
Drop-in replacement for S.db (MongoDB motor) with the same async interface.
Uses asyncpg for direct Postgres access to Supabase.
"""

import os
import json
import asyncpg
import uuid
from datetime import datetime, timezone

class SupabaseCollection:
    """Mimics MongoDB collection operations on a Postgres table."""
    
    def __init__(self, conn, table_name, primary_key='id'):
        self.conn = conn
        self.table = table_name
        self.pk = primary_key
    
    def _sanitize_filter(self, filter_dict):
        """Convert MongoDB filter syntax to simple WHERE conditions."""
        # Handle simple cases only: {key: value}, {key: {: ..., : i}}
        conditions = []
        values = []
        for key, val in filter_dict.items():
            if isinstance(val, dict):
                if '$regex' in val:
                    pattern = val['$regex']
                    if val.get('$options') == 'i':
                        conditions.append(f'LOWER({key}::text) LIKE LOWER($%d)' % (len(values) + 1))
                        values.append(f'%{pattern}%')
                    else:
                        conditions.append(f'{key}::text LIKE $%d' % (len(values) + 1))
                        values.append(f'%{pattern}%')
                elif '$gte' in val:
                    conditions.append(f'{key} >= $%d' % (len(values) + 1))
                    values.append(val['$gte'])
                elif '$lte' in val:
                    conditions.append(f'{key} <= $%d' % (len(values) + 1))
                    values.append(val['$lte'])
                elif '$in' in val:
                    placeholders = ','.join(['$%d' % (len(values) + i + 1) for i in range(len(val['$in']))])
                    conditions.append(f'{key} IN ({placeholders})')
                    values.extend(val['$in'])
                else:
                    conditions.append(f'{key} = $%d' % (len(values) + 1))
                    values.append(json.dumps(val))
            else:
                conditions.append(f'{key}::text = $%d' % (len(values) + 1))
                values.append(str(val))
        return conditions, values
    
    def _doc_to_row(self, doc):
        """Convert MongoDB document to Postgres column values."""
        cols = []
        vals = []
        for k, v in doc.items():
            if k == '_id':
                continue
            cols.append(k)
            if isinstance(v, (dict, list)):
                vals.append(json.dumps(v))
            elif isinstance(v, bool):
                vals.append(v)
            elif isinstance(v, datetime):
                vals.append(v.isoformat())
            else:
                vals.append(v)
        return cols, vals
    
    def _row_to_doc(self, row, mongo_id_field=None):
        """Convert Postgres row dict to MongoDB-like document."""
        doc = {}
        for k, v in row.items():
            if isinstance(v, uuid.UUID):
                doc[k] = str(v)
            elif isinstance(v, str):
                try:
                    doc[k] = json.loads(v)
                except:
                    doc[k] = v
            else:
                doc[k] = v
        if mongo_id_field and mongo_id_field in doc:
            doc['_id'] = doc.pop(mongo_id_field)
        return doc
    
    async def find_one(self, filter_dict=None, projection=None):
        """Find a single document."""
        if filter_dict is None:
            filter_dict = {}
        conditions, values = self._sanitize_filter(filter_dict)
        where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
        
        cols = '*'
        if projection and isinstance(projection, dict):
            cols = ', '.join([k for k, v in projection.items() if v])
        
        query = f'SELECT {cols} FROM {self.table}{where} LIMIT 1'
        try:
            row = await self.conn.fetchrow(query, *values)
            return dict(row) if row else None
        except Exception as e:
            print(f'Supabase find_one error ({self.table}): {e}')
            return None
    
    async def find(self, filter_dict=None, sort=None, skip=0, limit=0, projection=None):
        """Find multiple documents."""
        if filter_dict is None:
            filter_dict = {}
        conditions, values = self._sanitize_filter(filter_dict)
        where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
        
        order = ''
        if sort:
            parts = []
            for s in sort:
                field = s[0]
                direction = 'ASC' if len(s) < 2 or s[1] == 1 else 'DESC'
                parts.append(f'{field} {direction}')
            if parts:
                order = ' ORDER BY ' + ', '.join(parts)
        
        limit_clause = f' LIMIT {limit}' if limit > 0 else ''
        offset_clause = f' OFFSET {skip}' if skip > 0 else ''
        
        query = f'SELECT * FROM {self.table}{where}{order}{limit_clause}{offset_clause}'
        try:
            rows = await self.conn.fetch(query, *values)
            return [dict(r) for r in rows]
        except Exception as e:
            print(f'Supabase find error ({self.table}): {e}')
            return []
    
    async def insert_one(self, document):
        """Insert a document."""
        if 'id' not in document and '_id' not in document:
            document['id'] = str(uuid.uuid4())
        cols, vals = self._doc_to_row(document)
        placeholders = ', '.join([f'${i+1}' for i in range(len(cols))])
        cols_str = ', '.join(cols)
        query = f'INSERT INTO {self.table} ({cols_str}) VALUES ({placeholders}) RETURNING *'
        try:
            row = await self.conn.fetchrow(query, *vals)
            return dict(row) if row else None
        except Exception as e:
            print(f'Supabase insert_one error ({self.table}): {e}')
            return None
    
    async def update_one(self, filter_dict, update_dict):
        """Update a document."""
        conditions, c_values = self._sanitize_filter(filter_dict)
        where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
        
        if '$set' in update_dict:
            update_dict = update_dict['$set']
        
        set_parts = []
        set_values = []
        for k, v in update_dict.items():
            set_parts.append(f'{k} = ${len(c_values) + len(set_values) + 1}')
            if isinstance(v, (dict, list)):
                set_values.append(json.dumps(v))
            elif isinstance(v, bool):
                set_values.append(v)
            else:
                set_values.append(str(v))
        
        query = f'UPDATE {self.table} SET {", ".join(set_parts)}{where}'
        try:
            await self.conn.execute(query, *c_values, *set_values)
            return True
        except Exception as e:
            print(f'Supabase update_one error ({self.table}): {e}')
            return False
    
    async def delete_one(self, filter_dict):
        """Delete a document."""
        conditions, values = self._sanitize_filter(filter_dict)
        where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
        query = f'DELETE FROM {self.table}{where}'
        try:
            await self.conn.execute(query, *values)
            return True
        except Exception as e:
            print(f'Supabase delete_one error ({self.table}): {e}')
            return False
    
    async def count_documents(self, filter_dict=None):
        """Count documents."""
        if filter_dict is None:
            filter_dict = {}
        conditions, values = self._sanitize_filter(filter_dict)
        where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
        query = f'SELECT COUNT(*) as c FROM {self.table}{where}'
        try:
            row = await self.conn.fetchrow(query, *values)
            return row['c'] if row else 0
        except Exception as e:
            print(f'Supabase count error ({self.table}): {e}')
            return 0
    
    async def distinct(self, field, filter_dict=None):
        """Get distinct values."""
        conditions = []
        values = []
        if filter_dict:
            conditions, values = self._sanitize_filter(filter_dict)
        where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
        query = f'SELECT DISTINCT {field} FROM {self.table}{where}'
        try:
            rows = await self.conn.fetch(query, *values)
            return [r[field] for r in rows]
        except Exception as e:
            print(f'Supabase distinct error ({self.table}): {e}')
            return []
    
    async def aggregate(self, pipeline):
        """Basic aggregation support."""
        # Only handles simple $match + $group + $sort
        try:
            match = next((s.get('$match', {}) for s in pipeline if '$match' in s), {})
            group = next((s.get('$group', {}) for s in pipeline if '$group' in s), None)
            sort = next((s.get('$sort', {}) for s in pipeline if '$sort' in s), None)
            
            conditions, values = self._sanitize_filter(match)
            where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
            
            if group:
                group_id = group.get('_id')
                group_fields = ', '.join([f'{op}({field}) as {name}' for name, spec in group.items() if name != '_id' and isinstance(spec, dict) for op, field in spec.items()])
                if not group_fields:
                    group_fields = 'COUNT(*) as count'
                query = f'SELECT {group_id or 1} as _id, {group_fields} FROM {self.table}{where} GROUP BY {group_id or 1}'
            else:
                query = f'SELECT * FROM {self.table}{where}'
            
            if sort:
                order_parts = [f'{k} {DESC if v == -1 else ASC}' for k, v in sort.items()]
                query += ' ORDER BY ' + ', '.join(order_parts)
            
            rows = await self.conn.fetch(query, *values)
            return [dict(r) for r in rows]
        except Exception as e:
            print(f'Supabase aggregate error ({self.table}): {e}')
            return []


class SupabaseDB:
    """Replacement for S.db — provides MongoDB-style collection access."""
    
    TABLES = {
        'admin_users': 'admin_users',
        'customer_accounts': 'customer_accounts',
        'contacts': 'contacts',
        'leads': 'leads',
        'crm_leads': 'crm_leads',
        'quotes': 'quotes',
        'invoices': 'invoices',
        'documents': 'documents',
        'signatures': 'signatures',
        'chat_sessions': 'chat_sessions',
        'chat_files': 'chat_files',
        'messages': 'messages',
        'conversations': 'conversations',
        'nexify_ai_conversations': 'nexify_ai_conversations',
        'nexify_ai_messages': 'nexify_ai_messages',
        'analytics': 'analytics',
        'audit_log': 'audit_log',
        'timeline_events': 'timeline_events',
        'webhook_events': 'webhook_events',
        'health_checks': 'health_checks',
        'counters': 'counters',
        'email_events': 'email_events',
        'forms': 'forms',
        'form_submissions': 'form_submissions',
        'outbound_auto_runs': 'outbound_auto_runs',
        'trigger_runs': 'trigger_runs',
        'newsletter_subscribers': 'newsletter_subscribers',
        'chat_hub': 'chat_hub',
        'whatsapp_sessions': 'whatsapp_sessions',
        'access_links': 'access_links',
    }
    
    def __init__(self):
        self._pool = None
        self._conn = None
    
    async def connect(self, dsn=None):
        """Initialize connection pool."""
        if not dsn:
            dsn = os.environ.get(
                'ALT_SUPABASE_POSTGRESQL',
                'postgresql://postgres:f6a3d6778ca8a12038ff71a8fab8d174@127.0.0.1:5435/postgres?sslmode=disable'
            )
        self._conn = await asyncpg.connect(dsn)
        print(f'SupabaseDB connected: {dsn[:50]}...')
    
    async def close(self):
        if self._conn:
            await self._conn.close()
    
    def __getattr__(self, name):
        """Return a SupabaseCollection for the given table name."""
        table = self.TABLES.get(name, name)
        if not self._conn:
            raise Exception('SupabaseDB not connected. Call connect() first.')
        return SupabaseCollection(self._conn, table)
