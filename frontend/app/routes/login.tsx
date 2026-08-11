import React, { useState } from "react";
import { login } from "../../services/auth";

export default function Login() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    

    


    const handleSubmit = async (e : React.FormEvent) => {
        e.preventDefault()
        const user = await login(email, password)
        console.log(user);
        
    }

    return (
    <form onSubmit={ handleSubmit }>
        <input type="email" name="email" onChange={(e) => {
            setEmail(e.target.value)
        } }/>
        <input type="password" name="password" onChange={(e) => {
            setPassword(e.target.value)
        } }/>
        <button type="submit">Login</button>
    </form>
  );
}
