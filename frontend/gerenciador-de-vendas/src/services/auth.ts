
interface TokenResponse{
    access_token: string;
    token_type: string;
}

export async function login(email: string, password: string): Promise<string> {
    const bodyData = new URLSearchParams();
    bodyData.append('username', email);
    bodyData.append('password', password);

    const response = await fetch('http://localhost:8000/token', {
        method: 'Post',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: bodyData,
    });

    if (!response.ok){
        throw new Error('Login fail, verify your email or password.');
    }

    const data: TokenResponse = await response.json();

    localStorage.setItem('token', data.access_token);

    return data.access_token;
}