
'use client'
import {useState} from 'react'
import catalog from '@/data/catalog.json'

export default function Player(){
 const lectures=catalog
 const [current,setCurrent]=useState(lectures[0])
 const index=lectures.findIndex(l=>l.id===current.id)
 const prev=index>0?lectures[index-1]:null
 const next=index<lectures.length-1?lectures[index+1]:null

 return(
 <div style={{maxWidth:900,margin:'40px auto'}}>
  <h1 style={{fontSize:32,fontWeight:'bold'}}>Project ALBACAT</h1>
  <h2 style={{marginTop:20}}>{current.title}</h2>

  <audio controls autoPlay style={{width:'100%',marginTop:10}} key={current.audioUrl}>
   <source src={current.audioUrl} type="audio/mpeg"/>
  </audio>

  <div style={{marginTop:10,display:'flex',gap:10}}>
   <button onClick={()=>prev&&setCurrent(prev)}>Previous</button>
   <button onClick={()=>next&&setCurrent(next)}>Next</button>
   <a href={current.audioUrl}>Download</a>
  </div>

  <h3 style={{marginTop:30}}>Playlist</h3>
  {lectures.map(l=>(
   <div key={l.id} style={{marginTop:10}}>
    <button onClick={()=>setCurrent(l)}>{l.title}</button>
   </div>
  ))}
 </div>
 )
}
