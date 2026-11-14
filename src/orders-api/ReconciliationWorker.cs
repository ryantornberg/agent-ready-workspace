namespace Orders.Api;

/// <summary>Runs once a night and matches each day's payments to its orders.</summary>
public sealed class ReconciliationWorker
{
    private readonly IOrderStore _orders;

    public ReconciliationWorker(IOrderStore orders)
    {
        _orders = orders;
    }

    public async Task<int> RunAsync(DateOnly day, CancellationToken cancel)
    {
        var unmatched = await _orders.UnmatchedPaymentsAsync(day, cancel);
        return unmatched.Count;
    }
}
