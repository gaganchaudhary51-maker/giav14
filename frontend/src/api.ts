const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
async function request(path:string,init:RequestInit={}){const token=localStorage.getItem("gia_token");const headers=new Headers(init.headers);if(!headers.has("Content-Type"))headers.set("Content-Type","application/json");if(token)headers.set("Authorization",`Bearer ${token}`);const r=await fetch(`${API}${path}`,{...init,headers});const b=await r.json().catch(()=>({}));if(!r.ok)throw new Error(b.detail||"Request failed");return b}
export const api={
signup:(name:string,email:string,password:string)=>request("/auth/signup",{method:"POST",body:JSON.stringify({name,email,password})}),
login:(email:string,password:string)=>request("/auth/login",{method:"POST",body:JSON.stringify({email,password})}),
me:()=>request("/auth/me"),
projects:async()=>{const r=await request("/projects");return r.projects||r.items||[]},
createProject:(name:string,description:string)=>request("/projects",{method:"POST",body:JSON.stringify({name,description})}),
plan:(text:string,project_id?:string)=>request("/conversation/plan",{method:"POST",body:JSON.stringify({text,project_id})}),
events:()=>request("/events/recent?limit=30"),
voiceProviders:()=>request("/voice/providers"),
voiceStart:(project_id?:string)=>request("/voice/sessions",{method:"POST",body:JSON.stringify({project_id,provider:"browser",mode:"hands-free"})}),
voiceState:(id:string,state:string)=>request(`/voice/sessions/${id}/state`,{method:"POST",body:JSON.stringify({state})}),
voiceTranscript:(id:string,text:string)=>request(`/voice/sessions/${id}/transcript`,{method:"POST",body:JSON.stringify({text})})
};