import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface Props extends Omit<React.ComponentProps<typeof Card>, "title"> {
  title: string;
  description?: React.ReactNode;
}

/** A dashboard card whose title is a real heading, so screen readers can jump between sections. */
export function Section({ title, description, children, ...props }: Props) {
  return (
    <Card {...props}>
      <CardHeader>
        <CardTitle role="heading" aria-level={2}>
          {title}
        </CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
