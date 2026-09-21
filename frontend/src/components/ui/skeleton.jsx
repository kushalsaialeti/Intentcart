import React from "react";

export function Skeleton({ className = "", ...props }) {
  return (
    <div
      className={`animate-pulse rounded-md bg-[#27272a] ${className}`}
      {...props}
    />
  );
}

export default Skeleton;
