import React, { useState } from 'react';
import axios from '../api/axiosConfig';

const AddDataForm = () => {
    const [content, setContent] = useState('');
    const [message, setMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('/add-data', { content });
            setMessage(response.data.message);
        } catch (error) {
            setMessage('Error: Unable to add data.');
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <label>
                    Content:
                    <input
                        type="text"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        required
                    />
                </label>
                <button type="submit">Submit</button>
            </form>
            {message && <p>{message}</p>}
        </div>
    );
};

export default AddDataForm;
