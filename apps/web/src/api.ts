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
export async function uploadMedia(file:File){
  const signed=await request<{assetId:string;uploadUrl:string;headers:Record<string,string>}>('/api/v1/media/presign',{method:'POST',body:JSON.stringify({filename:file.name,contentType:file.type,byteSize:file.size})});
  const upload=await fetch(signed.uploadUrl,{method:'PUT',headers:signed.headers,body:file});
  if(!upload.ok)throw new Error('Media upload failed');
  await request(`/api/v1/media/${signed.assetId}/complete`,{method:'POST'});
  return signed.assetId;
}
export async function publishPost(post:{title:string;caption:string;category:string;type:string;assetId?:string}){const result=await request<{item:{id:string}}>('/api/v1/content',{method:'POST',body:JSON.stringify({title:post.title,caption:post.caption,category:post.category,assetId:post.assetId,media:{type:post.type.toLowerCase()}})});return result.item}
export async function submitReview(contentId:string,rating:number,body:string){return request(`/api/v1/content/${contentId}/reviews`,{method:'POST',body:JSON.stringify({rating,body})})}
export async function submitComment(contentId:string,body:string,parentId?:string){return request(`/api/v1/content/${contentId}/comments`,{method:'POST',body:JSON.stringify({body,parentId})})}
export async function joinGroup(groupId:string){return request(`/api/v1/groups/${groupId}/join`,{method:'POST'})}
export async function leaveGroup(groupId:string){return request<void>(`/api/v1/groups/${groupId}/membership`,{method:'DELETE'})}
export async function inviteToGroup(groupId:string,email:string,role='MEMBER'){return request(`/api/v1/groups/${groupId}/invites`,{method:'POST',body:JSON.stringify({email,role})})}
export async function joinEvent(eventId:string,role:'ATTENDEE'|'PERFORMER'='ATTENDEE'){return request(`/api/v1/events/${eventId}/join`,{method:'POST',body:JSON.stringify({role})})}
export async function leaveEvent(eventId:string){return request<void>(`/api/v1/events/${eventId}/attendance`,{method:'DELETE'})}
export async function createEvent(input:{title:string;description:string;startsAt:string;capacity:number}){return request('/api/v1/events',{method:'POST',body:JSON.stringify(input)})}
export async function listConversations(){return request('/api/v1/conversations')}
export async function listMessages(conversationId:string){return request(`/api/v1/conversations/${conversationId}/messages`)}
export async function sendMessage(conversationId:string,body:string){return request(`/api/v1/conversations/${conversationId}/messages`,{method:'POST',body:JSON.stringify({body})})}
export async function purchaseMarketplaceItem(itemId:string,idempotencyKey:string){return request<{balance:number}>(`/api/v1/marketplace/${itemId}/purchase`,{method:'POST',body:JSON.stringify({idempotencyKey})})}
