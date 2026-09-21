import * as React from "react";

const Input = React.forwardRef(({ className = "", type = "text", ...props }, ref) => {
  return (
    <input
      type={type}
      className={`flex h-11 w-full rounded-xl border border-[#E5E5E5] bg-white px-3.5 py-2 text-sm sm:text-base text-[#171717] placeholder:text-[#A3A3A3] shadow-2xs transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:border-[#171717] focus-visible:ring-2 focus-visible:ring-[#171717]/10 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      ref={ref}
      {...props}
    />
  );
});

Input.displayName = "Input";

export { Input };
export default Input;
