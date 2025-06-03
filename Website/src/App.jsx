import { useState } from 'react'
import LLMForm from './LLMForm'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <LLMForm/>
    </>
  )
}

export default App
