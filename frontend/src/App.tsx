import React from "react"
import QRGenerators from "./components/QRGenerators"
import Tracker from "./components/Tracker"
import Header from "./components/Header"
import VideoViewer from "./components/VideoViewer"

const pages = [
  {tabId: 0, label: 'Card Generator', component: <QRGenerators />},
  {tabId: 1, label: 'Library', component: <VideoViewer />},
  {tabId: 2, label: 'Tracker', component: <Tracker />},
  {tabId: 3, label: 'Settings', component: <div>Settings</div>},
]


function App() {
  const [tabId, setTabId] = React.useState(0)
  return (
    <>
      <Header setTabId={setTabId} pages={pages} />
      {pages[tabId].component}
    </>
  )
}

export default App;