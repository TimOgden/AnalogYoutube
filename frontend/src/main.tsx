import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter } from "react-router";
import { RouterProvider } from "react-router/dom";

import ResponsiveAppBar from "./App";
import QRGenerator from "./components/QRGenerator";
import Tracker from "./components/Tracker";

import "./index.css";

const router = createBrowserRouter([
    {
        path: "/",
        Component: QRGenerator,
    },
    {
        path: "/tracking",
        Component: Tracker,
    },
]);

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <ResponsiveAppBar />
        <RouterProvider router={router} />
    </StrictMode>,
);