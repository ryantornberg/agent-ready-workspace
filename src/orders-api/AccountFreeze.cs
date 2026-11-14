namespace Orders.Api;

/// <summary>A hold on an account: orders are accepted and not shipped until it is lifted.</summary>
public record AccountFreeze(Guid AccountId, string Reason, DateTimeOffset PlacedAt)
{
    public bool IsLifted { get; init; }

    public AccountFreeze Lift() => this with { IsLifted = true };
}

public interface IOrderStore
{
    Task<IReadOnlyList<Payment>> UnmatchedPaymentsAsync(DateOnly day, CancellationToken cancel);
}

public record Payment(Guid OrderId, decimal Amount);
