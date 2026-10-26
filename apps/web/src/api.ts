const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:4000';

export type ApiUser = { id?:string; name:string; handle:string; email?:string; categories?:string[]; diamonds?:number };

async function request<T>(path:string, init:RequestInit = {}):Promise<T>{
  const response=await fetch(`${API_URL}${path}`,{...init,credentials:'include',headers:{'content-type':'application/json',...init.headers},signal:AbortSignal.timeout(1800)});
  if(!response.ok){const body=await response.json().catch(()=>({}));throw new Error(body.error||`Request failed (${response.status})`)}
  return response.status===204?undefined as T:response.json() as Promise<T>;
}

export async function restoreSession(){return (await request<{user:ApiUser}>('/api/v1/auth/me')).user}
export async function registerAccount(input:{name:string;email:string;password:string}){return (await request<{user:ApiUser}>('/api/v1/auth/register',{method:'POST',body:JSON.stringify(input)})).user}
export async function logoutAccount(){return request<void>('/api/v1/auth/logout',{method:'POST'})}
export async function saveInterests(categories:string[]){return (await request<{user:ApiUser}>('/api/v1/profile',{method:'PATCH',body:JSON.stringify({categories})})).user}
export async function publishPost(post:{title:string;caption:string;category:string;type:string}){const result=await request<{item:{id:string}}>('/api/v1/content',{method:'POST',body:JSON.stringify({title:post.title,caption:post.caption,category:post.category,media:{type:post.type.toLowerCase()}})});return result.item}
