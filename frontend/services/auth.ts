import { api } from ".";

export async function login(email: string, password: string){

    try {
        const response = await api.post("/auth/token", {
            username:email,
            password
        }, { headers: {"Content-Type": "application/x-www-form-urlencoded"} })
        return response.data
    } catch (error) {
        console.log(error)
    }
}