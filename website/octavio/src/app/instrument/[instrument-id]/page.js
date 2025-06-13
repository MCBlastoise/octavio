'use client';

import { useParams } from 'next/navigation'
import InstrumentDisplay from '@/components/InstrumentDisplay';
import Box from '@mui/material/Box';

export default function InstrumentPage() {
    const params = useParams();
    const instrumentID = params["instrument-id"];
    return (
        <InstrumentDisplay instrument_id={instrumentID} />
    );
}
