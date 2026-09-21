import React from "react";
import { Button } from "@/components/ui/button";
import { Field } from "@/components/ui/field";
import { Input } from "@/components/ui/input";

export function InputInline({
  placeholder = "Search...",
  value,
  onChange,
  onSubmit,
  buttonText = "Search",
  disabled = false,
  className = "",
  ...props
}) {
  const handleSubmit = (e) => {
    e?.preventDefault();
    if (onSubmit) onSubmit(value);
  };

  return (
    <form onSubmit={handleSubmit} className={`w-full ${className}`}>
      <Field orientation="horizontal">
        <Input
          type="search"
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          disabled={disabled}
          {...props}
        />
        <Button type="submit" disabled={disabled}>
          {buttonText}
        </Button>
      </Field>
    </form>
  );
}

export default InputInline;
