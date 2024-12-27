import React, { useEffect, useState } from 'react';
import axios from '../api/axiosConfig';

const DisplayData = () => {
    const [data, setData] = useState({});
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('/data');
                setData(response.data);
            } catch (error) {
                setError('Error: Unable to fetch data.');
            }
        };

        fetchData();
    }, []);

    return (
        <div>
            {error ? <p>{error}</p> : <p>{JSON.stringify(data)}</p>}
        </div>
    );
};

export default DisplayData;
