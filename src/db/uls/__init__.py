import asyncpg as pg
import db.uls.defs
import datetime
import asyncio

def _ulsdate(ulsdate: str | None) -> datetime.date | None:
    if ulsdate is None:
        return None
    
    month, day, year = [ int(e) for e in ulsdate.split('/') ]
    return datetime.date(year, month, day)

class AmateurLicense:    
    def __init__(self, record: pg.Record):
        self._record = record
    
    @property
    def id(self) -> int:
        return self._record['unique_system_identifier']
    
    @property
    def _status(self) -> str:
        return self._record['license_status']
    
    @property
    def status(self) -> str:
        return defs.license_status(self._status)
    
    @property
    def _grant_date(self) -> str | None:
        return self._record['grant_date']

    @property
    def grant_date(self) -> datetime.date:
        return _ulsdate(self._grant_date)

    @property
    def _expire_date(self) -> str | None:
        return self._record['expired_date']

    @property
    def expire_date(self) -> datetime.date:
        return _ulsdate(self._expire_date)
    
    @property
    def _cancel_date(self) -> str | None:
        return self._record['cancellation_date']

    @property
    def cancel_date(self) -> datetime.date:
        return _ulsdate(self._cancel_date)
    
    @property
    def _effective_date(self) -> str | None:
        return self._record['effective_date']

    @property
    def effective_date(self) -> datetime.date:
        return _ulsdate(self._effective_date)
    
    @property
    def _last_action_date(self) -> str | None:
        return self._record['last_action_date']

    @property
    def last_action_date(self) -> datetime.date:
        return _ulsdate(self._last_action_date)
    
    @property
    def entity_type(self) -> str:
        return self._record['entity_type']

    @property
    def entity_name(self) -> str:
        return self._record['entity_name']

    @property
    def first_name(self) -> str:
        return self._record['first_name']

    @property
    def middle_initial(self) -> str:
        return self._record['mi']

    @property
    def last_name(self) -> str:
        return self._record['last_name']

    @property
    def suffix(self) -> str:
        return self._record['suffix']

    @property
    def name(self):
        name_components = [self.first_name, self.middle_initial, self.last_name, self.suffix]
        
        return ' '.join(filter(None, name_components)) or self.entity_name

    @property
    def street_address(self) -> str:
        return self._record['street_address']

    @property
    def city(self) -> str:
        return self._record['city']

    @property
    def state(self) -> str:
        return self._record['state']

    @property
    def _zip(self) -> str:
        return self._record['zip_code']
    
    @property
    def zip(self) -> str:
        z = self._zip
        
        if z and z.strip() and len(z.strip()) > 5:
            z = z.strip()
            return f"{z[:5]}-{z[5:]}"
        
        return z
    
    @property
    def _po_box(self) -> str:
        return self._record['po_box']
    
    @property
    def po_box(self) -> str:
        if self._po_box is None:
            return None
        
        return f"P.O. Box {self._po_box}"

    @property
    def _attn_line(self) -> str:
        return self._record['attention_line']

    @property
    def attn_line(self) -> str:
        if self._attn_line is None:
            return None

        return f"ATTN: {self._attn_line}"
    
    @property
    def frn(self) -> str:
        return self._record['frn']
    
    @property
    def _applicant_type(self) -> str:
        return self._record['applicant_type_code']
    
    @property
    def applicant_type(self) -> str:
        return defs.applicant_type(self._applicant_type)
    
    @property
    def callsign_ascii(self) -> str:
        if self._record['callsign'] is None:
            return None
        
        return self._record['callsign'].strip()
    
    @property
    def callsign(self) -> str:
        return self.callsign_ascii.replace('0', '\u00d8')
    
    @property
    def _operator_class(self) -> str:
        return self._record['operator_class']
    
    @property
    def operator_class(self) -> str:
        if self._operator_class is None:
            return None
        
        return defs.operator_class(self._operator_class)
    
    @property
    def trustee_callsign_ascii(self) -> str | None:
        if self._record['trustee_callsign'] is None:
            return None
        
        return self._record['trustee_callsign'].strip()
    
    @property
    def trustee_callsign(self) -> str | None:
        if self.trustee_callsign_ascii is None:
            return None

        return self.trustee_callsign_ascii.replace('0', '\u00d8')

    @property
    def trustee_name(self) -> str:
        return self._record['trustee_name']

class UlsClient:
    def __init__(self, pool: pg.pool.Pool):
        self.pool = pool
    
    async def license_by_callsign(self, callsign: str) -> AmateurLicense | None:
        async with self.pool.acquire() as conn:
            stmt = await conn.prepare("""SELECT unique_system_identifier, license_status,
    grant_date, expired_date, cancellation_date, effective_date, last_action_date,
    entity_type, entity_name, first_name, mi, last_name, suffix,
    street_address, city, state, zip_code, po_box, attention_line, frn, applicant_type_code,
    callsign, operator_class, trustee_callsign, trustee_name
    from l_HD JOIN l_EN USING(unique_system_identifier) JOIN l_AM using(unique_system_identifier)
    where l_HD.call_sign = $1::text ORDER BY to_date(effective_date, 'MM/DD/YYYY') DESC LIMIT 1;""")
            
            lic = await stmt.fetchrow(callsign.strip().upper())
            
            return AmateurLicense(lic) if lic is not None else None
        
    async def latency(self):
        start_ts = datetime.datetime.now()
        await self.license_by_callsign('W0EEE')
        end_ts = datetime.datetime.now()
        
        lookup_latency = end_ts - start_ts
        lookup_us = (lookup_latency.seconds * 10e6) + lookup_latency.microseconds
        lookup_ms = lookup_us / 1000
        
        return lookup_ms
