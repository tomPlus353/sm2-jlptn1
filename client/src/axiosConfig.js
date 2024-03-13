import axios from 'axios';

const instance = axios.create({
    baseURL: 'http://192.168.128.171:5000',
})

export default instance;