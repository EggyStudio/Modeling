using System.Reflection;
using Xunit;

namespace Modeling.Tests;

public class LibraryTests
{
    [Fact]
    public void The_Library_Loads()
    {
        // By its name rather than by a type of its own, which the library has none of yet, so the
        // test reads that the project reference puts the assembly beside the tests.
        var library = Assembly.Load("Modeling");
        Assert.Equal("Modeling", library.GetName().Name);
    }
}
