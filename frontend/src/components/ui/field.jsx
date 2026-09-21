import * as React from "react";

export function Field({
  children,
  className = "",
  orientation = "vertical",
  ...props
}) {
  const isHorizontal = orientation === "horizontal";
  return (
    <div
      className={`flex ${
        isHorizontal
          ? "flex-row items-center gap-2 w-full"
          : "flex-col gap-1.5 w-full"
      } ${className}`}
      data-orientation={orientation}
      {...props}
    >
      {children}
    </div>
  );
}

export function FieldLabel({ children, className = "", ...props }) {
  return (
    <label
      className={`text-sm font-medium text-[#171717] leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className}`}
      {...props}
    >
      {children}
    </label>
  );
}

export function FieldDescription({ children, className = "", ...props }) {
  return (
    <p className={`text-xs text-[#737373] ${className}`} {...props}>
      {children}
    </p>
  );
}

export default Field;
