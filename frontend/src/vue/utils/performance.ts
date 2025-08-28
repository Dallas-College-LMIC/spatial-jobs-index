export function measurePerformance(name: string, fn: () => void): void {
  const startTime = performance.now();
  fn();
  const endTime = performance.now();
  console.log(`${name} took ${endTime - startTime}ms`);
}
