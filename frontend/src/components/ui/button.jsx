import * as React from "react";

const Button = React.forwardRef(
  (
    {
      className = "",
      variant = "default",
      size = "default",
      type = "button",
      children,
      disabled = false,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-semibold transition-all duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#171717] focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 cursor-pointer active:scale-98 select-none";

    const variants = {
      default: "bg-[#171717] text-white hover:bg-[#262626] shadow-xs",
      secondary: "bg-[#F3F3F0] text-[#171717] hover:bg-[#E5E5E5] border border-[#E5E5E5]",
      outline: "border border-[#E5E5E5] bg-white text-[#171717] hover:bg-[#F3F3F0] shadow-2xs",
      ghost: "hover:bg-[#F3F3F0] text-[#171717]",
    };

    const sizes = {
      default: "h-11 px-5 py-2.5",
      sm: "h-9 rounded-lg px-3 text-xs",
      lg: "h-12 rounded-xl px-7 text-base",
      icon: "h-11 w-11 p-0",
    };

    const variantClass = variants[variant] || variants.default;
    const sizeClass = sizes[size] || sizes.default;

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled}
        className={`${baseStyles} ${variantClass} ${sizeClass} ${className}`}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";

export { Button };
export default Button;
